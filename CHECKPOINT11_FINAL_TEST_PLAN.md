# USB Guardian — Checkpoint 11: Final Product Test Plan

**Document Version:** 1.0  
**Date:** November 5, 2026  
**Auditor / Architect:** Senior Windows Security Engineer & QA Lead  
**Scope:** Staging, Release Candidate (RC) Verification, and Production Readiness  

---

## 1. Test Strategy & Scope

This test plan defines the complete verification regimen required to certify USB Guardian for final production deployment. Testing is divided into two distinct execution tiers:
1. **Tier 1 (Automated Regression & Userland QA):** Executed in isolated environments without risk to host Windows login credentials. (Fully automated with 76 passing tests).
2. **Tier 2 (Staging & Live OS Verification):** Performed on dedicated staging hardware prior to production rollout, covering live workstation locking and Safe Mode validation.

---

## 2. Test Execution Matrix

| Test ID | Test Category | Target Subsystem | Prerequisites | Expected Pass Criteria | Execution Tier |
|:---:|---|---|---|---|:---:|
| **TP-01** | USB Provisioning | `KeyManager`, `SecureStorage` | Unregistered USB drive | Ed25519 keypair generated; `token_metadata.json` and `private_key.enc` written atomically; public key recorded in SQLite. | Tier 1 (Automated) |
| **TP-02** | Passphrase Complexity | `Validation` | GUI Registration View | Passphrases $<8$ characters or with weak entropy are rejected with clear error prompts. | Tier 1 (Automated) |
| **TP-03** | Ed25519 Challenge-Response | `Authenticator`, `ChallengeManager` | Registered USB token | 32-byte CSPRNG challenge signed; signature verified; state transitions to `AUTHORIZED`. | Tier 1 (Automated) |
| **TP-04** | Anti-Replay Defense | `ChallengeManager` | Expired/Consumed Nonce | Replaying a previously used challenge ID or nonce $>60$s is rejected; returns `None`. | Tier 1 (Automated) |
| **TP-05** | Hardware Serial Binding | `Authenticator`, `USBDetector` | Cloned USB drive files | Drive with identical files but different SCSI controller serial is rejected (`Hardware identity mismatch`). | Tier 1 (Automated) |
| **TP-06** | System Drive Exclusion | `USBDetector` | `C:\` and `D:\` drives | System partition and internal NVMe/fixed disks are never categorized as removable USB tokens. | Tier 1 (Automated) |
| **TP-07** | Physical Removal Watchdog | `USBMonitor` | Authenticated session | Detaching USB token immediately initiates monotonic 5.0-second countdown; logs `USB_REMOVED`. | Tier 1 (Automated) |
| **TP-08** | Glitch & Bus Re-enumeration | `USBMonitor` | Transient disconnect | Brief bus reconnection before countdown expiry halts grace period; requires fresh challenge-response. | Tier 1 (Automated) |
| **TP-09** | Simulated Lock Execution | `WindowsSessionLocker` | Simulation mode enabled | When countdown reaches 0.0s, session transitions to `WORKSTATION_LOCKED`; `real_locks = 0`. | Tier 1 (Automated) |
| **TP-10** | Database Tamper-Evidence | `DatabaseManager` | SQLite database | Modifying, inserting, or deleting rows manually causes `verify_log_chain_integrity()` to fail. | Tier 1 (Automated) |
| **TP-11** | Zero Plaintext Leakage | Raw storage & logs | USB NAND & SQLite | Neither Windows passwords nor unencrypted private keys exist in logs or on the USB drive. | Tier 1 (Automated) |
| **TP-12** | IPC Bearer Token Security | `IPCServer`, `IPCClient` | TCP loopback socket | Connections without valid 256-bit token or exceeding 64 KB payload are rejected with 401 error. | Tier 1 (Automated) |
| **TP-13** | Mutex Single-Instance | `BackgroundService` | Named Win32 Mutex | Spawning a secondary daemon process aborts with `RuntimeError("Another instance running")`. | Tier 1 (Automated) |
| **TP-14** | Pre-Logon 2FA Packaging | `poc_serialization.py` | Win32 Secur32 | `MSV1_0_INTERACTIVE_LOGON` payload formatted with Package ID 11 and valid Unicode offsets. | Tier 1 (Automated) |
| **TP-15** | Live Workstation Locking | `WindowsSessionLocker` | Staging Machine | Simulation disabled: pulling USB locks desktop via `user32.LockWorkStation` leaving apps running. | Tier 2 (Staging Only) |
| **TP-16** | Safe Mode Immunity | Winlogon Subsystem | Staging Machine | Machine boots into Safe Mode; third-party Credential Provider is bypassed; standard password works. | Tier 2 (Staging Only) |
| **TP-17** | WinRE Emergency Recovery | Windows Recovery Env | Staging Machine | Single `reg delete` command cleanly removes provider registration without data loss. | Tier 2 (Staging Only) |

---

## 3. Staging & Acceptance Criteria

### Production Gate 1: Core Application Release (Desktop & Daemon)
- **Criteria:** All Tier 1 tests (**TP-01 through TP-14**) must achieve a 100% pass rate.
- **Current Status:** **MET (76 / 76 Tests Passing with Zero Warnings)**.

### Production Gate 2: Pre-Login Credential Provider Release
- **Criteria:** 
  1. Build machine equipped with Visual Studio 2022 Community x64 build tools and Windows 11 SDK.
  2. Native compilation of `USBGuardianCredentialProvider.dll` succeeds without warnings.
  3. Tier 2 tests (**TP-15 through TP-17**) successfully executed on a staging PC without lockout incidents.
- **Current Status:** **PENDING DEDICATED BUILD MACHINE**.

