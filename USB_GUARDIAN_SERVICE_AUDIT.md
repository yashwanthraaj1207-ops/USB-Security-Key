# USB Guardian — Background Service Audit Report

**Component**: Background Access Watchdog Daemon & IPC Server  
**Modules Audited**:
- [`windows/service/background_service.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/windows/service/background_service.py)
- [`windows/service/ipc_server.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/windows/service/ipc_server.py)
- [`windows/session_lock.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/windows/session_lock.py)

---

## 1. Watchdog & Detection Lifecycle Audit

The [`BackgroundService`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/windows/service/background_service.py#L26) operates an autonomous daemon loop:
1. **Startup**: Initializes [`DatabaseManager`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/database/db_manager.py#L33), loads persistent configuration, verifies simulation mode defaults (`simulation_mode = true`), and binds the IPC loopback server on port 52331.
2. **Monitoring**: Instantiates [`USBMonitor`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/core/usb_monitor.py#L18) in a dedicated background thread, scanning device storage buses at $1.0\text{s}$ intervals.
3. **Shutdown**: Registers POSIX signal handlers (`SIGINT`, `SIGTERM`) on Windows to invoke `self.stop()`, which terminates worker threads within $2.0\text{s}$ timeouts and releases OS mutex handles.

---

## 2. IPC Protocol & Security Architecture

### Cryptographic Token Authentication
- **Token Generation**: Upon service launch, [`IPCServer`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/windows/service/ipc_server.py#L22) generates a 256-bit CSPRNG token using `secrets.token_hex(32)`.
- **Token Storage**: Persisted to `%LOCALAPPDATA%\USBGuardian\.ipc_token` with restrictive file permissions.
- **Timing-Attack Resistance**: Token verification utilizes `secrets.compare_digest()`, eliminating timing side-channels during token string comparison.
- **Access Rule**:
  - `PING`: Unauthenticated health check permitted for daemon readiness probes.
  - All other commands (`GET_STATE`, `AUTHENTICATE`, `START_MONITOR`, `STOP_MONITOR`, `GET_LOGS`, `VERIFY_LOGS`, `GET_CONFIG`): Strictly require the valid 256-bit authorization token. Requests with invalid or missing tokens return `{"status": "UNAUTHORIZED"}`.

### DoS & Buffer Overflow Mitigations
- **Payload Limit**: Enforces a strict $64\text{ KB}$ ceiling (`client_sock.recv(65536)`). Requests exceeding this limit or malformed JSON are rejected without memory exhaustion.
- **Command Whitelisting**: Commands not in `ALLOWED_COMMANDS` are rejected immediately.

---

## 3. Duplicate Instance Prevention (Mutex Guard)

To prevent duplicate processes from causing race conditions, corrupted states, or conflicting port binds:
- The daemon creates a named Win32 kernel mutex: `Local\USBGuardian_BackgroundService_Mutex`.
- If a second instance launches, Win32 `GetLastError()` returns `ERROR_ALREADY_EXISTS` (183).
- The duplicate process immediately aborts with `RuntimeError("Another instance of USB Guardian Background Service is already running.")` and releases handles safely.

---

## 4. Interactive Session Routing & Session 0 Isolation

Windows isolates background services in Session 0:
- If a service executes under `LocalSystem` (Session 0), `user32.LockWorkStation()` targets the non-interactive Session 0 desktop.
- **Solution**: USB Guardian runs as a per-user daemon inside the active interactive session (Session 1), invoked via the user's startup registry key. This guarantees that workstation lock requests act directly on the active desktop screen displaying `LogonUI`.

---

## 5. Database Durability & Crash Resilience

- **WAL Mode**: SQLite operates in Write-Ahead Logging (`WAL`) mode with `synchronous = NORMAL`.
- **Atomic Transactions**: All operations in [`DatabaseManager`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/database/db_manager.py#L33) run within context-managed `_connection_scope()`.
- **Integrity**: Even in an abrupt process termination (`taskkill /F`), uncommitted transactions are rolled back atomically by the SQLite engine, preventing corrupt database states.

