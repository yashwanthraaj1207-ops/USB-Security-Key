# USB Guardian — Checkpoint 12: Bugs, Vulnerabilities & Fixes Register

**Document Version:** 1.0  
**Date:** November 5, 2026  
**Auditor / Architect:** Senior Windows Security Engineer & Systems Programmer  
**Scope:** Exhaustive Master Register of Discovered Defects, Security Vulnerabilities, and Applied Fixes  

---

## 1. Master Defects & Corrections Register

| Bug ID | Severity | Component | Defect Description | Root Cause | Correction Applied |
|:---:|:---:|---|---|---|---|
| **BUG-01** | **CRITICAL** | [`USBGuardianCredentialProvider.cpp:100`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/windows/credential_provider/USBGuardianCredentialProvider.cpp#L100) | Access Violation (0xC0000005) in `GetFieldDescriptorAt`. | Dereferenced `(*ppcpfd)->pszLabel` while `*ppcpfd` was NULL. In COM, `ppcpfd` is an out-parameter. | Allocated struct via `CoTaskMemAlloc(sizeof(CREDENTIAL_PROVIDER_FIELD_DESCRIPTOR))` before copying strings with `SHStrDupW`. |
| **BUG-02** | **HIGH** | [`core/session_manager.py:115`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/core/session_manager.py#L115) | Reconnection auto-authorization bypass. | Reconnecting the USB before the 5s grace period expired auto-restored `AUTHORIZED` without cryptographic verification. | Updated `set_usb_connected()` to set `status = CONNECTED_UNAUTHENTICATED` and `_is_authenticated = False`. Fresh challenge-response is mandatory. |
| **BUG-03** | **HIGH** | [`windows/service/ipc_server.py:65`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/windows/service/ipc_server.py#L65) | Unauthenticated loopback IPC access. | IPC server accepted all TCP connections without verifying authentication token. | Enforced 256-bit bearer token validated in constant time via `secrets.compare_digest` and command whitelisting. |
| **BUG-04** | **HIGH** | [`database/db_manager.py:90`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/database/db_manager.py#L90) | Plaintext database log tampering vulnerability. | SQLite logs could be modified or deleted directly in the database file without detection. | Implemented HMAC-SHA256 hash chaining (`prev_hash`, `entry_hash`) with persistent secret key and `verify_log_chain_integrity()`. |
| **BUG-05** | **MEDIUM** | [`windows/credential_provider/poc_serialization.py:165`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/windows/credential_provider/poc_serialization.py#L165) | Unhandled out-of-bounds string offset in serialization unpacking. | In Python, slicing `payload[99999:99999+10]` returns `b""` instead of raising an error. | Added explicit bounds verification `d_off + d_len > len(payload)` raising `ValueError` on truncated or malformed buffers. |
| **BUG-06** | **MEDIUM** | [`windows/service/background_service.py:40`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/windows/service/background_service.py#L40) | Background daemon simulation mode override hazard. | Daemon initialized with `simulate_lock=False` by default, risking accidental real locking. | Defaulted `simulate_lock=None`, which queries the persistent SQLite `simulation_mode` setting (defaulting to `"true"`). |
| **BUG-07** | **MEDIUM** | [`windows/service/ipc_server.py:100`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/windows/service/ipc_server.py#L100) | Unhandled `UnicodeDecodeError` crash on IPC fuzzing. | Raw socket read `.decode('utf-8')` threw unhandled exception on invalid UTF-8 bytes (`\xff\xfe`). | Wrapped decode in `try-except UnicodeDecodeError`, returning structured JSON error `{"status": "ERROR", "message": "Malformed JSON payload: Invalid character encoding"}`. |
| **BUG-08** | **LOW** | [`pytest.ini:1`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/pytest.ini) | Upstream third-party deprecation warning. | Pytest 9.2 emitted `PytestRemovedIn10Warning` triggered by `anyio.pytest_plugin`. | Configured `pytest.ini` with targeted filter `ignore::pytest.PytestRemovedIn10Warning:anyio\.pytest_plugin`. |
| **BUG-09** | **LOW** | [`app/authentication_view.py:25`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/app/authentication_view.py#L25), `README.md` | Inaccurate cryptographic terminology. | UI and docs described Ed25519 digital signatures as "Zero-Knowledge Authentication". | Audited and corrected terminology to **Asymmetric Ed25519 Digital Signature Challenge-Response**. |

---

## 2. Independent Code Consistency & Architecture Audit

### 2.1. `threading.Lock` vs `threading.RLock`
- **Audit Finding:** In `core/authenticator.py`, `database/db_manager.py`, and `core/session_manager.py`, `threading.Lock()` is utilized for synchronization.
- **Analysis:** We audited every method in these classes to check whether any method holding the lock calls another public method on the same instance that attempts to re-acquire the lock (recursive acquisition).
- **Result:** **No re-entrancy deadlocks exist.** In `database/db_manager.py`, methods such as `verify_log_chain_integrity()` execute direct SQL queries inside their own lock scope rather than calling `get_logs()`. The code is clean and deadlock-free.

### 2.2. IPC Architecture Alignment
- **Audit Finding:** Checked documentation for clarity regarding the two distinct IPC mechanisms:
  1. **Userland Desktop IPC:** Communicates between the PySide6 GUI and `BackgroundService` over local loopback TCP (`127.0.0.1:49152`) with 256-bit bearer token authentication.
  2. **Pre-Logon Session 0 IPC:** Communicates between `LogonUI.exe` and `BackgroundService` over a Windows Named Pipe (`\\.\pipe\USBGuardian_Logon`) with a restricted `SYSTEM` Security Descriptor.
- **Result:** Both communication channels are clearly distinguished in documentation and threat models.

