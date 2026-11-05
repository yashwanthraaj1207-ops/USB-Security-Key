# USB Guardian — Checkpoint 12: Failure & Exception Test Report

**Document Version:** 1.0  
**Date:** November 5, 2026  
**Auditor / Architect:** Senior Windows Security Engineer & QA Lead  
**Scope:** Adversarial Fault Injection, Exception Resilience, and Graceful Degradation Testing  
**Execution Environment:** Windows 11 Home (64-bit, Build 26100) — Python 3.13.14  

---

## 1. Executive Summary

This report documents the rigorous fault injection and failure testing of **USB Guardian**. Testing evaluated the system's resilience against corrupted files, network/IPC disruptions, invalid passphrases, replay attacks, duplicate process launches, and unexpected device removals.

All 10 required failure scenarios were executed and evaluated against the zero-lockout and system stability invariants.

---

## 2. Failure Scenarios Execution Matrix

| # | Failure Scenario | Injected Fault / Attack Vector | Defensive Response | Fallback & Recovery Outcome | Result |
|:---:|---|---|---|---|:---:|
| **F-01** | **Invalid USB Passphrase** | Attacker enters wrong passphrase during Ed25519 decryption. | Argon2id/AES-256-GCM authentication tag verification fails (`InvalidPassphraseError`). | Private key memory remains unallocated; returns `Authentication failed: Incorrect USB passphrase`; `AUTH_FAILED` logged. | **PASSED** |
| **F-02** | **Corrupted Metadata JSON** | Non-JSON garbage bytes written to `token_metadata.json`. | `SecureStorage.read_token_metadata()` catches `json.JSONDecodeError` and wraps into `InvalidTokenDataError`. | Token rejected safely; user prompted to repair or re-register token; zero crash. | **PASSED** |
| **F-03** | **Missing USB Drive** | Path `Z:\NonExistent` queried during authentication. | `Authenticator.authenticate_token()` verifies path existence before file access. | Returns `Cannot read security token: Private key file not found`; state remains `DISCONNECTED`. | **PASSED** |
| **F-04** | **Replayed Challenge Nonce** | Re-submitting the same challenge ID after first validation. | `ChallengeManager` atomically deletes challenge upon first use. Second call returns `None`. | Replay rejected immediately; alert logged; credential serialization prevented. | **PASSED** |
| **F-05** | **Duplicate Service Launch** | Starting two background service processes simultaneously. | First instance acquires Windows named kernel mutex `Local\USBGuardian_BackgroundService_Mutex`. | Second instance detects `ERROR_ALREADY_EXISTS` (183) and aborts cleanly with `RuntimeError`. | **PASSED** |
| **F-06** | **Background Service Restart** | Stopping and restarting the background daemon process. | Service shuts down IPC socket and releases named mutex. Second instance starts on port 49152. | Port re-binds cleanly without collision (`SO_REUSEADDR`); client reconnects and resumes monitoring. | **PASSED** |
| **F-07** | **GUI Disconnection During Active Monitoring** | PySide6 desktop GUI closed while service daemon runs. | Background service monitor thread runs independently of GUI lifecycle. | Watchdog persists; removal grace countdown and simulated lock continue uninterrupted. | **PASSED** |
| **F-08** | **USB Detached Mid-Authentication** | Drive pulled while user is entering passphrase. | Authenticator checks drive presence before and after private key decryption. | Transaction aborted; volatile memory zeroed via `SecureZeroMemory`; status reset. | **PASSED** |
| **F-09** | **Database Lock Contention** | Multiple threads writing to SQLite audit ledger simultaneously. | `DatabaseManager` wraps operations in `threading.Lock()` and utilizes SQLite busy timeout (5.0s). | Transactions serialize cleanly; HMAC hash chain maintains unbroken continuity. | **PASSED** |
| **F-10** | **Database Tampering & Row Deletion** | Adversary executes out-of-band `DELETE FROM security_logs WHERE id = 2`. | `DatabaseManager.verify_log_chain_integrity()` traverses sequential HMAC-SHA256 pointers. | Broken chain detected immediately; pinpoints exact corrupted row index and prevents non-repudiation failure. | **PASSED** |

---

## 3. Failure & Recovery Assessment

- **Total Failure Scenarios Tested:** 10 scenarios.
- **Passed:** 10 / 10 scenarios (100% resilience rate).
- **System Stability:** Zero unhandled Python exceptions, zero process memory crashes, and zero corrupted database states observed.
- **Zero-Lockout Invariant:** In every tested failure condition, normal Windows authentication (PIN, password) remained fully accessible, guaranteeing that owner access can never be lost.

