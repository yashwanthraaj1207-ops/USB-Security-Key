# USB Guardian — Checkpoint 10: Security Review & Threat Analysis

**Document Version:** 1.0  
**Date:** November 5, 2026  
**Auditor / Architect:** Senior Windows Security Engineer & Cybersecurity Architect  
**Scope:** Threat Modeling, Physical Hardware Boundaries, Session 0 Security, and Defensive Countermeasures  

---

## 1. Physical USB Security & The Commodity Hardware Boundary

### 1.1. The Reality of Commodity USB Flash Drives
A foundational responsibility of a Senior Cybersecurity Architect is avoiding false security claims:
> **Ordinary USB flash drive serial numbers ARE NOT cryptographic hardware identities.**

A commodity USB flash drive (such as our registered HP v232w or a SanDisk Ultra):
1. **Lacks Secure Hardware Enclaves:** Unlike smart cards, TPM chips, or FIDO2 security keys (YubiKey), commodity flash drives contain standard flash controllers (e.g., Phison, SMI, Alcor) with read/write NAND flash.
2. **Inquiry String Spoofing:** When Windows issues `IOCTL_STORAGE_QUERY_PROPERTY` or SCSI `INQUIRY` commands, the controller firmware returns vendor, product, and serial number strings. 
3. **Hardware Emulation Attacks:** Microcontroller boards (such as Raspberry Pi Pico, Facedancer21, Teensy, or GreatFET) can emulate USB mass storage devices and return arbitrary hardware serials and volume IDs.

### 1.2. Multi-Attribute Defense-in-Depth
Because commodity USB serial numbers can theoretically be emulated by dedicated hardware attackers, USB Guardian enforces **Multi-Attribute Defense-in-Depth**:
- **Layer 1: Physical Controller Inquiry Serial:** Verified via `IOCTL_STORAGE_QUERY_PROPERTY` to defeat file copy attacks.
- **Layer 2: Partition Volume Serial:** Verified against the registered filesystem serial number.
- **Layer 3: Cryptographic Key Encryption:** The Ed25519 private key on the drive is encrypted with Argon2id ($m=64\text{ MiB}, t=3, p=4$) and AES-256-GCM. An attacker who steals or clones the physical device still cannot sign challenges without the user's secret passphrase.
- **Layer 4: Digital Signature Verification:** The laptop verifies that incoming challenge responses are signed by the unique Ed25519 private key matching the public key enrolled in `%ProgramData%\USBGuardian\keys\`.
- **Layer 5: User Windows Password (2FA):** Even if an attacker cloned the USB and obtained the USB passphrase, they still cannot log in without the user's secret Windows password.

---

## 2. Replay Protection & Nonce Lifecycle

To prevent man-in-the-middle or passive replay attacks on the pre-logon Named Pipe:
1. **CSPRNG Generation:** Every challenge consists of 32 bytes of cryptographically secure random bytes generated via `os.urandom(32)` (`BCryptGenRandom` under the hood).
2. **Strict Expiration (60 Seconds):** Nonces are stamped with a monotonic timestamp. Any signature submitted after 60 seconds is rejected with `CHALLENGE_EXPIRED`.
3. **One-Time Consumption:** The challenge is atomically deleted from memory upon the first verification attempt. Subsequent attempts submitting the same challenge ID return `None` (verified by `test_challenge_replay_blocks_serialization`).

---

## 3. Credential Theft & Memory Security

Pre-logon authentication processes sensitive credentials in memory (`USB passphrase`, `Windows password`, `decrypted Ed25519 private key`). The following protections are enforced:
1. **In-Memory Zeroing:**
   - In C++: Both `_pszPassphrase` and `_pszWindowsPassword` are wiped using Windows `SecureZeroMemory` prior to `CoTaskMemFree`:
     ```cpp
     if (_pszWindowsPassword) {
         SecureZeroMemory(_pszWindowsPassword, wcslen(_pszWindowsPassword) * sizeof(WCHAR));
         CoTaskMemFree(_pszWindowsPassword);
         _pszWindowsPassword = nullptr;
     }
     ```
   - In Python: Decrypted Ed25519 private key bytes are stored in mutable `bytearray` objects and overwritten with zeros in `finally` blocks before deletion (verified by `test_buffer_allocation_and_memory_zeroing`).
2. **Session 0 Isolation:**
   - `LogonUI.exe` and the USB Guardian Background Service execute in **Session 0**, which is isolated from unprivileged interactive user processes (`Session 1+`).
   - Standard user applications cannot attach debuggers (`CreateRemoteThread`, `VirtualAllocEx`) or read memory (`ReadProcessMemory`) of Session 0 processes without `SeDebugPrivilege`.

---

## 4. Service IPC Authorization & Named Pipe Security

The communication channel between `LogonUI.exe` and the Background Service uses a Windows Named Pipe (`\\.\pipe\USBGuardian_Logon`):
1. **Explicit Security Descriptor (DACL):**
   The pipe is created by the background service with a restricted Security Descriptor granting access strictly to:
   - `NT AUTHORITY\SYSTEM` (`GENERIC_ALL`)
   - `NT AUTHORITY\INTERACTIVE` (`GENERIC_READ | GENERIC_WRITE`)
   - Denies access to standard unprivileged network or remote callers.
2. **Caller Process Validation:**
   The background service queries `GetNamedPipeClientProcessId()` to verify that the connecting process is `LogonUI.exe` located in `C:\Windows\System32\`.
3. **Payload Sanitization:**
   Incoming JSON commands are restricted to a 64 KB maximum payload size and validated against a strict command whitelist (`GET_CHALLENGE`, `AUTH_REQUEST`).

---

## 5. Failure Handling & Removal During Authentication

| Failure Mode | Trigger Condition | Defensive Response | Fallback Result |
|---|---|---|---|
| **USB Removed Mid-Auth** | Flash drive pulled out while user is typing password or during signature verification. | `WM_DEVICECHANGE` triggers immediate cancellation. In-flight signature aborted; memory zeroed; tile resets status to *"USB Removed"*. | User reinserts USB or clicks "Sign-in options" to log in with Windows PIN. |
| **Passphrase Mistyped** | User mistypes USB token passphrase. | Argon2id/AES-GCM tag verification fails. Private key never decrypted; `AUTH_FAILED` committed to HMAC audit log. | User re-enters passphrase or switches to Windows PIN tile. |
| **Windows Password Incorrect** | User enters wrong Windows account password. | `MSV1_0` rejects NTLM hash. `LogonUI` receives `STATUS_LOGON_FAILURE` (`0xC000006D`). | User re-enters Windows password. |
| **Background Service Crash** | Service terminated or stopped by administrator. | Credential Provider pipe connection times out (3.0s). Tile displays *"Service Unavailable"*. | User switches to standard Windows Password / PIN tile. |
| **USB Damaged / Lost** | Physical USB NAND failure or drive lost. | `GetCredentialCount()` returns `0`. USB Guardian tile is hidden or disabled. | **Unbreakable Fallback:** User logs in with native Windows Password or PIN. |

---

## 6. Security Classification Matrix

| Security Claim | Verification Level | Evidence / Justification |
|---|:---:|---|
| Multi-attribute serial binding defeats casual file copying | **UNIT TESTED** | Verified in `test_usb_cloning_simulation` and `test_invalid_hardware_identity`. |
| Ordinary USB flash drive is clone-proof against microcontroller emulators | **FALSE (Rejected)** | Acknowledged physical boundary: Hardware emulators can spoof USB inquiry strings. |
| Nonces are strictly single-use and resist replay attacks | **UNIT TESTED** | Verified in `test_challenge_replay_blocks_serialization`. |
| Windows passwords are never stored on the USB drive | **UNIT TESTED** | Verified by inspecting raw NAND storage in `test_zero_windows_credentials_stored_on_usb`. |
| C++ passphrase and password buffers are zeroed in memory | **IMPLEMENTED** | Audited in `CProviderCredential::~CProviderCredential` (`SecureZeroMemory`). |
| Windows authentication occurs via official MSV1_0 package | **RESEARCHED & SIMULATED** | Validated via `poc_serialization.py` and `LsaLookupAuthenticationPackage` (Package ID: 11). |
| Workstation lockout cannot occur from USB Guardian failure | **UNIT TESTED** | Verified non-exclusive provider registration and Safe Mode bypass. |

