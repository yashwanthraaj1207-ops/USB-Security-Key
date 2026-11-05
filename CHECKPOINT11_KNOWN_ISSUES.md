# USB Guardian — Checkpoint 11: Known Issues & Technical Limitations

**Document Version:** 1.0  
**Date:** November 5, 2026  
**Auditor / Architect:** Senior Windows Security Engineer & Cybersecurity Architect  
**Status:** Comprehensive Technical Risk & Boundary Registry  

---

## 1. Physical Hardware & Cryptographic Boundaries

### ISSUE-01: Commodity USB Flash Drives Lack Cryptographic Enclaves
- **Severity:** High (Physical Security Boundary)
- **Component:** USB Hardware Token
- **Description:** A commodity USB flash drive (such as our registered HP v232w) contains a standard mass storage microcontroller with writable NAND flash. It possesses no secure cryptoprocessor, TPM, or smart card chip.
- **Attack Vector:** An attacker with dedicated hardware (e.g., Facedancer21, Raspberry Pi Pico running custom USB device descriptor firmware) can clone the SCSI inquiry serial and partition volume ID.
- **Mitigation & Impact:** USB Guardian binds both the controller serial and volume serial, defeating all file-level copy attacks. Furthermore, the private key is encrypted with Argon2id ($m=64\text{ MiB}, t=3, p=4$) and AES-256-GCM; even a cloned device cannot sign challenges without the user's secret passphrase. True hardware attestation, however, requires FIDO2/YubiKey smart cards.

---

## 2. Windows 11 Pre-Login Authentication & Credential Origin

### ISSUE-02: Windows 11 Local SAM Rejects Public-Key Only Logon
- **Severity:** Medium (OS Architectural Constraint)
- **Component:** Windows Credential Provider / `LSASS.exe`
- **Description:** Windows local accounts (`SAM`) authenticate exclusively via NTLM password hashes evaluated by `msv1_0.dll`. The SAM schema has no fields for public keys and `MSV1_0` has no digital signature engine.
- **Impact:** USB Guardian **cannot log into Windows using only a USB signature** without either:
  1. Requiring the user to enter their Windows password alongside the USB passphrase (**Approach 1: Two-Factor Authentication — Verified & Recommended**), or
  2. Storing an encrypted copy of the user's Windows password in a local TPM/DPAPI vault on the laptop disk (**Approach 3: Vaulted Credential Release**).
- **Mitigation:** Approach 1 (2FA) is selected as the default architecture, upholding the invariant: *"Never store the user's Windows password on the USB drive or disk."*

---

## 3. Host Build Environment & Toolchain State

### ISSUE-03: Host System Lacks 64-bit MSVC / Windows SDK Toolchain
- **Severity:** Medium (Build Dependency)
- **Component:** `windows/credential_provider/`
- **Description:** The current host machine has Python 3.13 and 32-bit MinGW GCC 6.3.0, but lacks Visual Studio 2022 Community, MSVC (`cl.exe`), and the Windows 11 SDK (`credentialprovider.h`).
- **Impact:** The C++ Credential Provider source code is fully implemented and audited, but **cannot be compiled into a native 64-bit DLL on this machine**.
- **Remediation:** Visual Studio 2022 Community with the "Desktop development with C++" workload and Windows 11 SDK must be installed on the build machine.

---

## 4. Workstation Locking & Simulation Mode Enforcement

### ISSUE-04: Lock Simulation Mode Enabled by Default
- **Severity:** Informational (Safety Constraint)
- **Component:** [`windows/session_lock.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/windows/session_lock.py), [`database/db_manager.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/database/db_manager.py)
- **Description:** `simulation_mode` is hardcoded and stored as `"true"` in SQLite. `WindowsSessionLocker` contains a hard execution guard (`if self.simulate: return True`).
- **Impact:** Removing the USB drive simulates locking and logs simulated events, but **does not invoke the live Win32 `user32.LockWorkStation` API**.
- **Remediation for Staging/Production:** To test real workstation locking during staging, an administrator must explicitly toggle Simulation Mode to `"false"` in the Settings tab.

---

## 5. Session 0 & IPC Boundary

### ISSUE-05: Background Service Requires SYSTEM Privileges for Pre-Login Pipe
- **Severity:** Low (Operational Deployment Constraint)
- **Component:** [`windows/service/background_service.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/windows/service/background_service.py)
- **Description:** In a pre-login environment, `LogonUI.exe` runs in Session 0 before any user logs in. The Named Pipe `\\.\pipe\USBGuardian_Logon` must be hosted by a service running as `NT AUTHORITY\SYSTEM`.
- **Impact:** When run as an interactive user process (`python main.py`), the background thread cannot interact with `LogonUI.exe`.
- **Remediation:** In production deployment, the background service is installed via Windows Service Control Manager (`sc.exe create USBGuardian binPath=...`) to run continuously in Session 0.

---

## 6. Single-Token Enrollment Model

### ISSUE-06: Database Schema Supports One Active Hardware Token
- **Severity:** Low (Feature Enhancement)
- **Component:** [`database/models.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/database/models.py), [`core/key_manager.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/core/key_manager.py)
- **Description:** The current database model and `KeyManager` store a single active registered token. Registering a new USB token marks previously registered tokens as inactive.
- **Impact:** Users cannot register multiple backup USB keys simultaneously for the same Windows workstation.
- **Future Roadmap:** Multi-token provisioning support is slated for Version 2.0.

