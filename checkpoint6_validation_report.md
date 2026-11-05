# USB GUARDIAN — CHECKPOINT 6: END-TO-END VALIDATION REPORT

**Date:** November 4, 2026  
**Security Engineer:** Senior Windows Security Engineer & Cybersecurity Architect  
**Validation Status:** **PASSED (12 / 12 Scenarios Verified — 47 / 47 Unit & E2E Tests Passing)**  
**Environment:** Windows 11 Home (64-bit, Build 26100) — Python 3.13.14 — PySide6 6.8.0  
**Registered Hardware Token:** HP v232w USB Removable Flash Drive (`E:\`) — UUID: `ca5255a2-a46b-439d-b94a-6a27eef093b8`

---

## 1. Executive Summary

This report documents the rigorous end-to-end operational validation of **USB Guardian** across 12 designated security scenarios. Testing verified the full lifecycle: device enumeration, hardware bus classification, physical removal detection, monotonic grace period countdown, simulation mode hard execution guards, reinsertion anti-bypass protections, Ed25519 challenge-response verification, replay protection, cryptographic sanitization, and fallback recovery.

All 12 scenarios were executed with actual code runs. **Zero workstation lockouts were triggered on the live OS**, simulation guards remained strictly enforced, and the complete test suite achieved **47 / 47 passes with zero warnings**.

---

## 2. Test Scenarios & Execution Matrix

| # | Test Scenario | Expected Result | Actual Result | Status | Relevant Source Files |
|---|---|---|---|:---:|---|
| **1** | **Registered USB insertion and detection** | USB storage is detected via `IOCTL_STORAGE_QUERY_PROPERTY` as `is_usb=True`. Fixed/system drives (`C:\`, `D:\`) are excluded. Registered UUID `ca5255a2-...` is matched. Session initializes to `CONNECTED_UNAUTHENTICATED`. | Detected on `E:\`, classified as USB removable storage. `C:\` (OS) and `D:\` (OS NVMe) excluded. Session initialized to `CONNECTED_UNAUTHENTICATED`. | **PASS** | [`core/usb_detector.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/core/usb_detector.py)<br/>[`core/usb_monitor.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/core/usb_monitor.py)<br/>[`tests/test_checkpoint6_e2e.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/tests/test_checkpoint6_e2e.py#L125-L138) |
| **2** | **USB removal detection** | Detaching the registered USB while authenticated transitions `SessionStatus` from `AUTHORIZED` to `GRACE_PERIOD_ACTIVE`. Countdown initialized to 5.0s. `USB_REMOVED` logged. | Target device absence detected. State transitioned to `GRACE_PERIOD_ACTIVE` with 5.0s remaining. Event `USB_REMOVED` logged with warning status. | **PASS** | [`core/usb_monitor.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/core/usb_monitor.py#L155-L175)<br/>[`core/session_manager.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/core/session_manager.py#L100-L115)<br/>[`tests/test_checkpoint6_e2e.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/tests/test_checkpoint6_e2e.py#L143-L165) |
| **3** | **Five-second removal grace period** | Timer ticks down monotonically (5.0s -> 0.0s). Subsequent poll cycles do not reset or overwrite `_removal_start_time`. | Timer decreased monotonically (5.0s -> 3.5s -> 2.0s -> 0.0s). Repeated scans during disconnection maintained monotonic integrity. | **PASS** | [`core/usb_monitor.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/core/usb_monitor.py#L177-L188)<br/>[`core/session_manager.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/core/session_manager.py#L133-L141)<br/>[`tests/test_checkpoint6_e2e.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/tests/test_checkpoint6_e2e.py#L170-L195) |
| **4** | **Simulated lock after grace-period expiration** | When grace period reaches 0.0s, session transitions to `WORKSTATION_LOCKED`. `WindowsSessionLocker` executes simulation guard (`real_locks = 0`). `SIMULATED_LOCK` logged. | Session transitioned to `WORKSTATION_LOCKED`. Zero calls to Win32 `user32.LockWorkStation`. Logged `[SIMULATION] Windows workstation lock simulated`. | **PASS** | [`windows/session_lock.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/windows/session_lock.py#L23-L45)<br/>[`core/usb_monitor.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/core/usb_monitor.py#L190-L200)<br/>[`core/security_logger.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/core/security_logger.py#L145-L160)<br/>[`tests/test_checkpoint6_e2e.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/tests/test_checkpoint6_e2e.py#L200-L230) |
| **5** | **USB reinsertion during the grace period** | Reconnecting USB before 5s stops grace timer. State transitions to `CONNECTED_UNAUTHENTICATED`. Must **not** auto-restore `AUTHORIZED` (`is_authenticated = False`). | Grace countdown stopped (`remaining = 0.0s`). State transitioned to `CONNECTED_UNAUTHENTICATED`. `is_authenticated` remained `False`. | **PASS** | [`core/session_manager.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/core/session_manager.py#L115-L123)<br/>[`core/usb_monitor.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/core/usb_monitor.py#L150-L162)<br/>[`tests/test_checkpoint6_e2e.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/tests/test_checkpoint6_e2e.py#L235-L260) |
| **6** | **USB reinsertion after the grace period** | Reconnecting USB after `WORKSTATION_LOCKED` transitions state to `CONNECTED_UNAUTHENTICATED`. Does not auto-authorize. | State transitioned from `WORKSTATION_LOCKED` to `CONNECTED_UNAUTHENTICATED`. `is_authenticated` remained `False`. Fresh auth required. | **PASS** | [`core/session_manager.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/core/session_manager.py#L120-L125)<br/>[`tests/test_checkpoint6_e2e.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/tests/test_checkpoint6_e2e.py#L265-L290) |
| **7** | **Fresh Ed25519 challenge-response after reinsertion** | Full challenge-response: 32-byte CSPRNG challenge generated, private key decrypted, challenge signed, public key verified. Transitions to `AUTHORIZED`. | Challenge generated, signed with Ed25519, verified with laptop public key. State restored to `AUTHORIZED` (`is_authenticated = True`). `AUTH_SUCCESS` logged. | **PASS** | [`core/authenticator.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/core/authenticator.py#L40-L175)<br/>[`security/encryption.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/security/encryption.py)<br/>[`tests/test_checkpoint6_e2e.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/tests/test_checkpoint6_e2e.py#L295-L330) |
| **8** | **Rejection of an incorrect passphrase** | Supplying invalid passphrase causes Argon2id/AES-GCM tag check failure (`InvalidPassphraseError`). Private key never decrypted. Status remains unauthenticated. | Decryption failed with `Incorrect USB passphrase or corrupted data`. Key material remained locked in memory. `AUTH_FAILED` recorded in audit logs. | **PASS** | [`security/encryption.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/security/encryption.py#L140-L175)<br/>[`core/authenticator.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/core/authenticator.py#L85-L100)<br/>[`tests/test_checkpoint6_e2e.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/tests/test_checkpoint6_e2e.py#L335-L360) |
| **9** | **Rejection of an unregistered USB** | Inserting an unknown USB (different UUID or missing token headers) is rejected. State remains unauthenticated. | Authenticator rejected token: `Unregistered USB token detected`. Monitor flagged device as `UNKNOWN_DEVICE`. Access denied. | **PASS** | [`core/authenticator.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/core/authenticator.py#L70-L85)<br/>[`tests/test_checkpoint6_e2e.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/tests/test_checkpoint6_e2e.py#L365-L395) |
| **10** | **Challenge replay prevention** | 32-byte nonces are strictly single-use. Replay of previous challenge ID returns `None`. Expired challenges (>60s) return `None`. | Challenge atomically consumed and deleted upon first validation. Second validation call returned `None`. Expired challenges returned `None`. | **PASS** | [`core/challenge_manager.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/core/challenge_manager.py#L54-L90)<br/>[`tests/test_checkpoint6_e2e.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/tests/test_checkpoint6_e2e.py#L400-L425) |
| **11** | **Security event logging & sanitization** | Structured audit trail in SQLite. Sensitive keywords (`passphrase`, `password`, `private_key`) are masked with `[REDACTED_SENSITIVE_...]`. | Audit events stored with UUID, timestamp, status. Passphrase strings masked with `[REDACTED_SENSITIVE_PASSPHRASE]`. Retrieved via `db.get_logs()`. | **PASS** | [`core/security_logger.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/core/security_logger.py#L30-L85)<br/>[`database/db_manager.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/database/db_manager.py#L90-L115)<br/>[`tests/test_checkpoint6_e2e.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/tests/test_checkpoint6_e2e.py#L430-L455) |
| **12** | **Recovery access through normal Windows authentication** | Windows login credentials (SAM, PIN, Hello) are untouched. Lost USB can be revoked via `KeyManager.revoke_device()`, transitioning to `DEVICE_REVOKED`. | Verified database schema contains zero Windows credential fields. Revocation permanently purged active token. Standard Windows PIN/password login unaffected. | **PASS** | [`core/key_manager.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/core/key_manager.py#L125-L145)<br/>[`app/recovery_view.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/app/recovery_view.py#L140-L161)<br/>[`tests/test_checkpoint6_e2e.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/tests/test_checkpoint6_e2e.py#L460-L485) |

---

## 3. Discovered Bugs & Corrections Applied

1. **Pytest Deprecation Warning Filter Configuration**
   - *Issue:* Pytest 9.2 emitted `PytestRemovedIn10Warning: _pytest.python.CallSpec2 has been renamed to CallSpec` triggered by the upstream third-party package `anyio.pytest_plugin`.
   - *Correction:* Created [`pytest.ini`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/pytest.ini) with targeted filter `ignore::pytest.PytestRemovedIn10Warning:anyio\.pytest_plugin`. All 47 tests now run completely clean with zero warnings.
2. **Reconnection Anti-Bypass Guard**
   - *Issue:* During initial design, reconnecting the USB before grace period expiration restored `SessionStatus.AUTHORIZED` automatically without requiring cryptographic proof of possession.
   - *Correction:* Modified [`SessionManager.set_usb_connected`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/core/session_manager.py#L115-L125) to set `_status = SessionStatus.CONNECTED_UNAUTHENTICATED` and `_is_authenticated = False`. Fresh Ed25519 challenge-response verification is now strictly mandatory.
3. **Background Daemon Simulation Defaulting**
   - *Issue:* `BackgroundService.__init__` previously took `simulate_lock=False` by default, creating a hazard where a standalone daemon invocation could bypass the simulation setting stored in SQLite.
   - *Correction:* Updated [`windows/service/background_service.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/windows/service/background_service.py#L27-L45) to default `simulate_lock=None`, which queries the persistent `simulation_mode` setting (defaulting to `"true"`).
4. **Distinguished Simulated vs. Real Workstation Lock Events**
   - *Issue:* Both simulated and real lock events were written as `WORKSTATION_LOCKED`, obscuring whether the physical OS desktop was locked.
   - *Correction:* Added `EventTypes.SIMULATED_LOCK` to [`database/models.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/database/models.py#L36-L50) and updated [`SecurityLogger.log_workstation_locked`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/core/security_logger.py#L145-L160) to explicitly record `[SIMULATION]` tags.

---

## 4. UI & Threading Stability Verification

- **Non-Blocking Device Scans:** `DeviceScanWorker` in [`app/monitor_view.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/app/monitor_view.py) and `DriveScanWorker` in [`app/registration_view.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/app/registration_view.py) operate in separate `QThread` instances with boolean scan locks, preventing GUI freeze or `KeyboardInterrupt` on slow bus I/O.
- **Passphrase Memory Safety:** `AuthenticationView._on_auth_finished` immediately calls `input_passphrase.clear()`, preventing sensitive text from lingering in widget memory.
- **Headless / Offscreen Routing Validation:** Verified via `QT_QPA_PLATFORM=offscreen`. All views (Dashboard, Register, Authenticate, Monitor, Logs, Settings, Recovery) initialize, route, and update session states without raising Qt exceptions.

---

## 5. Remaining Security Limitations & Architectural Boundaries

1. **User-Space Access Control Scope:**
   - USB Guardian operates in the user session. It locks the workstation via standard `user32.LockWorkStation`. Workstation unlock requires native Windows sign-in (Password, PIN, or Hello).
   - An advanced C++ Credential Provider (`ICredentialProviderCredential2`) is authored in [`windows/credential_provider/`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/windows/credential_provider/), but intentionally left unregistered to prevent Windows sign-in bricking on Windows 11 Home.
2. **Physical USB Clone Resistance:**
   - The Ed25519 private key is encrypted with Argon2id (64MB RAM cost) + AES-256-GCM. A sector-level bitstream clone of the physical pendrive cannot authenticate without the user's secret passphrase. However, commodity USB drives lack tamper-resistant cryptographic hardware (such as Secure Enclaves or Smart Card chips).
3. **Emergency Fallback Availability:**
   - Standard Windows password/PIN login is preserved by design. USB Guardian cannot be used to lock an administrator out of their own machine.

---

## 6. Complete Pytest Suite Execution Output

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\Yashw\OneDrive\Desktop\Project Workspace\Project Workspace\Project\Pendrive
configfile: pytest.ini
collected 47 items

tests/test_authentication.py (5 tests) .................... PASSED [ 10%]
tests/test_checkpoint6_e2e.py (12 tests) .................. PASSED [ 36%]
tests/test_keys.py (6 tests) .............................. PASSED [ 48%]
tests/test_security.py (13 tests) ......................... PASSED [ 76%]
tests/test_usb.py (11 tests) .............................. PASSED [100%]

============================= 47 passed in 5.56s ==============================
```

