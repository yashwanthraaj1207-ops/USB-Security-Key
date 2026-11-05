# USB Guardian — Comprehensive Security Audit Report

**Audit Scope**: End-to-End Cryptography, Device Integrity, and Attack Vector Resistance  
**Target Platform**: Microsoft Windows 11 / 10 AMD64  
**Audit Status**: **PASSED (With Documented Hardware Boundaries)**  

---

## 1. Threat Model & Attack Vector Evaluation

| Attack Vector | Countermeasure / Implementation | Test Status | Evaluation Detail |
| :--- | :--- | :---: | :--- |
| **Passphrase Brute Force** | Argon2id KDF ($64\text{ MB}$ RAM, $3$ iterations, $4$ threads) | **PASS** | Deriving a key requires $\sim0.45\text{s}$ CPU work on modern hardware; GPU/ASIC parallel brute force computationally unfeasible. |
| **Nonce / Challenge Replay** | 256-bit CSPRNG single-use challenges with 60s expiration | **PASS** | Validated challenges are marked consumed atomically. Replayed nonces are rejected ($0\%$ replay acceptance). |
| **File System Copying / Token Cloning** | Encrypted private key + Controller Serial Binding | **PASS** | Files copied to another flash drive are rejected due to hardware controller serial mismatch (`IOCTL_STORAGE_QUERY_PROPERTY`). |
| **Log Injection / Tampering** | Cryptographic HMAC-SHA256 log hash chaining | **PASS** | Any out-of-band modification or truncation in SQLite is detected immediately by `verify_log_chain_integrity()`. |
| **Unauthorized IPC Commands** | 256-bit CSPRNG token via `secrets.compare_digest()` | **PASS** | Commands lacking the authorization token are rejected (`UNAUTHORIZED`). |
| **IPC Buffer Overflow / DoS** | $64\text{ KB}$ maximum buffer ceiling + command whitelist | **PASS** | Oversized payloads and unwhitelisted commands are rejected before processing. |
| **Session Lockout Exploitation** | Native Windows sign-in preservation | **PASS** | Windows PIN, Password, and Windows Hello are never modified or disabled; user is never locked out of Windows. |

---

## 2. Commodity USB Hardware Limitations vs Smartcards

> [!CAUTION]
> **Commodity USB flash drives cannot provide tamper-proof hardware security.**

### The Physical Reality of Standard USB Storage
1. **Controller Serial Spoofing**:
   - The hardware serial reported via Win32 `IOCTL_STORAGE_QUERY_PROPERTY` originates from the USB mass storage controller firmware.
   - Commodity USB drives do not possess secure elements (SE), cryptographic co-processors, or physical unclonable functions (PUF).
   - An attacker equipped with programmable microcontroller hardware (e.g., Facedancer, Raspberry Pi Pico, or custom USB descriptors) can emulate the vendor ID, product ID, and serial string (`4238B45B`).
2. **Private Key Protection**:
   - Because physical flash memory can be cloned byte-for-byte by hardware readers, the security of the private key rests strictly upon the **Argon2id + AES-256-GCM cryptographic encryption**.
   - Even if the raw NAND flash is dumped or copied, the Ed25519 private key cannot be decrypted without the user's secret passphrase.
3. **Recommendation for Military / High-Assurance Deployments**:
   - For environments requiring zero-trust physical tamper resistance, organizations should deploy hardware-enforced FIDO2 / PIV / SmartCard tokens (e.g., YubiKey) where private keys are physically non-exportable from silicon.
   - For workstation access control against casual physical access, stolen laptops, and unauthorized walk-up tampering, USB Guardian's multi-attribute binding provides strong defense-in-depth.

