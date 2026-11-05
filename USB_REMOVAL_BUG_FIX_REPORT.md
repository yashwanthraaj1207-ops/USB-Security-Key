# USB Guardian — USB Removal Lock Bug: Bug Fix Report

**Document Version:** 1.0  
**Date:** November 5, 2026  
**Auditor / Security Architect:** Senior Windows Security Lead  
**Classification:** Defect Resolution & Architectural Hardening  
**Target Executable:** `dist/USB Guardian/USB Guardian.exe`  

---

## 1. Defect Summary & Resolution Overview

The critical USB removal lock bug where removing the physical HP v232w token did not initiate the 5-second grace period countdown or trigger simulated session locking has been completely resolved.

| Defect Area | Problem Description | Code Resolution |
|---|---|---|
| **Database Device State** | Test scripts revoked active physical token `ca5255a2...` and inserted test key `aa900280...`, causing physical USB on `E:\` to appear as `DISCONNECTED`. | Restored physical token record as `ACTIVE`, purged test rows, restored matching public key, and strictly isolated acceptance tests into temporary directories. |
| **Concurrency & Race Condition** | `USBMonitor._check_devices()` was called concurrently by `WM_DEVICECHANGE` (GUI thread) and `_monitor_loop` (background thread) without synchronization. | Added reentrant `self._scan_lock = threading.RLock()` and wrapped `_check_devices()` with `with self._scan_lock:`. |
| **Session Protection Flag** | `protection_active` in `SessionManager.get_state()` only checked `is_authenticated`, causing ambiguity during grace countdown. | Explicitly included `(self._is_authenticated or self._status == SessionStatus.GRACE_PERIOD_ACTIVE)`. |
| **UI State Reflection** | When workstation entered `WORKSTATION_LOCKED`, GUI dropped into `else:` and displayed `"● Standby"` in sidebar and status bar. | Added explicit branches for `WORKSTATION_LOCKED` across `MainWindow`, `DashboardView`, and `AuthenticationView`. |
| **Storage Path Coercion** | `KeyManager` accepted `storage_dir` as `str` but downstream code assumed `Path`, throwing `TypeError` on `/` operator. | Enforced `self.storage_dir = Path(storage_dir) if storage_dir else get_default_storage_dir()`. |

---

## 2. Detailed Code Modifications

### 2.1. Concurrency Synchronization in `core/usb_monitor.py`

```python
# Added reentrant scan lock in __init__
self._running = False
self._thread: Optional[threading.Thread] = None
self._lock = threading.Lock()
self._scan_lock = threading.RLock()

# Synchronized device inspection
def _check_devices(self):
    """Scans connected devices, tracks state changes, and processes grace periods."""
    with self._scan_lock:
        registered_device = self.key_manager.get_registered_device()
        ...
```

### 2.2. State Flag Correction in `core/session_manager.py`

```python
# Line 73 in core/session_manager.py
def get_state(self) -> SessionState:
    """Returns snapshot of current session state."""
    return SessionState(
        status=self._status,
        is_authenticated=self._is_authenticated,
        is_usb_connected=self._is_usb_connected,
        registered_device_uuid=self._registered_device_uuid,
        registered_device_name=self._registered_device_name,
        current_drive_letter=self._current_drive_letter,
        last_authenticated_time=self._last_auth_time,
        protection_active=self.auto_lock_enabled and (self._is_authenticated or self._status == SessionStatus.GRACE_PERIOD_ACTIVE),
        grace_period_remaining=self._grace_period_remaining,
        grace_period_total=self.grace_period_total,
    )
```

### 2.3. Path Normalization in `core/key_manager.py`

```python
# Line 34 in core/key_manager.py
def __init__(
    self,
    db_manager: DatabaseManager,
    security_logger: SecurityLogger,
    storage_dir: Optional[Path] = None,
):
    self.db = db_manager
    self.logger = security_logger
    self.storage_dir = Path(storage_dir) if storage_dir else get_default_storage_dir()
```

### 2.4. Sidebar & Status Bar State Handling in `app/main_window.py`

```python
# Lines 260-275 in app/main_window.py
if state.status == SessionStatus.WORKSTATION_LOCKED:
    self.lbl_sidebar_status.setText("● Workstation Locked")
    self.lbl_sidebar_status.setStyleSheet("color: #ef4444; font-size: 11px; padding: 0 16px; font-weight: 600;")
    self.status_bar.showMessage("Workstation locked automatically (Token Removed). Re-authentication required.")
elif state.status == SessionStatus.GRACE_PERIOD_ACTIVE:
    self.lbl_sidebar_status.setText("● Grace Countdown")
    self.lbl_sidebar_status.setStyleSheet("color: #f59e0b; font-size: 11px; padding: 0 16px; font-weight: 600;")
    self.status_bar.showMessage(f"WARNING: Token removed. Workstation auto-lock in {state.grace_period_remaining:.1f}s.")
elif state.is_authenticated:
    self.lbl_sidebar_status.setText("● System Secured")
    self.lbl_sidebar_status.setStyleSheet("color: #00e676; font-size: 11px; padding: 0 16px; font-weight: 600;")
    self.status_bar.showMessage("Physical USB Token Authorized. Continuous access watchdog engaged.")
else:
    self.lbl_sidebar_status.setText("● Standby")
    self.lbl_sidebar_status.setStyleSheet("color: #94a3b8; font-size: 11px; padding: 0 16px; font-weight: 600;")
    self.status_bar.showMessage("USB Guardian standing by. Insert registered physical token.")
```

### 2.5. Alert Banner State Handling in `app/dashboard.py`

```python
# Lines 254-260 in app/dashboard.py
if state.status == SessionStatus.WORKSTATION_LOCKED:
    self.alert_banner.setStyleSheet("background-color: #2e1010; border: 1px solid #dc2626;")
    self.lbl_alert.setText("🔒 Workstation Locked: Physical token was removed and grace period expired. Re-authentication required.")
    self.lbl_alert.setStyleSheet("font-weight: 700; color: #f87171;")
elif state.status == SessionStatus.GRACE_PERIOD_ACTIVE:
    ...
```

### 2.6. Authentication View Re-Verification Handling in `app/authentication_view.py`

```python
# Lines 190-210 in app/authentication_view.py
def update_state(self, state: SessionState):
    """Called whenever session state changes."""
    self.check_token_presence()
    if state.status == SessionStatus.WORKSTATION_LOCKED:
        self.btn_authenticate.setText("⚡ Verify Challenge-Response to Unlock Workstation")
        self.btn_authenticate.setProperty("class", "btn-primary")
        if not self._detected_drive:
            active = self.key_manager.get_registered_device()
            name = active.name if active else "USB Token"
            self.lbl_token_info.setText(
                f"🔒 Workstation is LOCKED due to USB removal.\n"
                f"Please insert '{name}' and verify your passphrase to unlock."
            )
    elif state.status == SessionStatus.GRACE_PERIOD_ACTIVE:
        self.btn_authenticate.setText(f"⚠️ Token Removed - Locking in {state.grace_period_remaining:.1f}s")
        self.btn_authenticate.setProperty("class", "btn-secondary")
    elif state.is_authenticated:
        self.btn_authenticate.setText("✅ Physical Token Authorized (Click to Re-verify)")
        self.btn_authenticate.setProperty("class", "btn-success")
    else:
        self.btn_authenticate.setText("⚡ Verify Challenge-Response & Authorize")
        self.btn_authenticate.setProperty("class", "btn-primary")
    self.btn_authenticate.style().unpolish(self.btn_authenticate)
    self.btn_authenticate.style().polish(self.btn_authenticate)
```

### 2.7. Complete Test Isolation in `acceptance_test_rc1.py`

```python
# Lines 89-94 in acceptance_test_rc1.py
_iso_dir = tempfile.mkdtemp(prefix="rc1_iso_")
_iso_db = Path(_iso_dir) / "test_acceptance.db"
_iso_keys = Path(_iso_dir) / "keys"
db = DatabaseManager(db_path=str(_iso_db))
logger = SecurityLogger(db)
km = KeyManager(db, logger, storage_dir=_iso_keys)
cm = ChallengeManager()
auth = Authenticator(km, cm, logger)
detector = USBDetector()
```

---

## 3. Production Database State Verification

Following the defect resolution, the live production database was inspected and verified:

```sql
SELECT id, uuid, name, serial_number, status FROM devices;
```

**Result:**
```
(1, 'ca5255a2-a46b-439d-b94a-6a27eef093b8', 'v232w Token', '4238B45B', 'ACTIVE')
```

- **Registered Token:** HP v232w (`ca5255a2-a46b-439d-b94a-6a27eef093b8`)
- **Status:** `ACTIVE`
- **Controller Serial Number:** `4238B45B`
- **Total Registered Devices in Production DB:** Exactly 1 (Zero dummy test devices).
- **Public Key File:** `%LOCALAPPDATA%\USBGuardian\keys\registered_public_key.pem` verified matching the active device record.

