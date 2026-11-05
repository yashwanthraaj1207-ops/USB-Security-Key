# USB Guardian — Critical USB Removal Lock Bug: Root Cause Analysis

**Document Version:** 1.0  
**Date:** November 5, 2026  
**Component:** `core.usb_monitor`, `core.session_manager`, `database.db_manager`, `app.main_window`  
**Classification:** Critical Security & UX Pipeline Defect  
**Status:** Resolved & Verified  

---

## 1. Executive Summary

During physical hardware testing on Windows 11 Home with the registered **HP v232w USB flash drive**, the following symptoms were observed:
1. The **Authentication View** displayed:
   - **Registered device:** `v232w Token`
   - **Device status:** `DISCONNECTED`
   - **Application status:** `Standby`
2. Physically removing the registered USB from the USB port did **not** trigger the expected five-second simulated lock event or record a `SIMULATED_LOCK` audit entry.

A deep architectural and forensic investigation identified **four compounding root causes**, with the primary driver being **production database device state corruption caused by test script execution**, compounded by a **multi-threaded race condition** in the USB monitoring loop and **GUI state reflection gaps**.

---

## 2. Root Cause Breakdown

### Root Cause 1: Production Database Device State Corruption (Primary Trigger)

#### Forensic Evidence
Querying the live production database at `%LOCALAPPDATA%\USBGuardian\database\usb_guardian.db` revealed the following rows in the `devices` table:

```sql
SELECT id, uuid, name, serial_number, registered_at, status FROM devices;
```

```
(1,  'ca5255a2-a46b-439d-b94a-6a27eef093b8', 'v232w Token',        '4238B45B',             '2026-11-04T17:30:44Z', 'REVOKED')
(2,  'dc9857b9-6922-4636-a8a0-07cecce7bbf1', 'RC1 Acceptance Test', 'ACCEPTANCE-HW-SN-001', '2026-11-04T19:30:48Z', 'REVOKED')
...
(15, 'aa900280-d997-49c8-8c27-0f372dbfb830', 'Rejection Test Key',  'REJECT-SN-001',        '2026-11-05T05:48:30Z', 'ACTIVE')
```

Furthermore, `%LOCALAPPDATA%\USBGuardian\keys\registered_public_key.pem` contained the public key corresponding to dummy token `aa900280...` rather than the physical HP v232w token `ca5255a2...`.

#### Failure Mechanism
1. Automated acceptance script `acceptance_test_rc1.py` instantiated `DatabaseManager()` and `KeyManager(db, logger)` without passing isolated temporary directory paths.
2. In `KeyManager.register_usb_token()`:
   ```python
   # Line 121-123 in core/key_manager.py
   existing = self.db.get_active_device()
   if existing:
       self.db.revoke_device(existing.uuid)
   ```
3. Each test run executed `UPDATE devices SET status = 'REVOKED' WHERE status = 'ACTIVE'` against the **live workstation database**, marking the physical HP v232w token (`ca5255a2...`) as `REVOKED`.
4. The test script then inserted dummy token `aa900280...` (`Rejection Test Key`) as `ACTIVE`.
5. When the user launched `USB Guardian` and connected their physical HP v232w USB drive:
   - The application loaded the active device record: `active_uuid = aa900280-d997-49c8-8c27-0f372dbfb830`.
   - The physical USB on `E:\` contained `E:\USB_GUARDIAN\token_metadata.json` with `device_uuid = ca5255a2-a46b-439d-b94a-6a27eef093b8`.
   - `USBDetector.find_device_by_uuid("aa900280...")` searched all drives and returned `None` because `ca5255a2... != aa900280...`.
   - `AuthenticationView.check_token_presence()` set the badge to `DISCONNECTED` and disabled the authentication button (`btn_authenticate.setEnabled(False)`).
   - Because the token could not be verified, `SessionManager.is_authenticated` remained `False`.
6. When the user unplugged the USB:
   - `USBMonitor._check_devices()` evaluated `was_auth = self.session.get_state().is_authenticated`.
   - Because `was_auth == False`, no grace period was started (`_removal_start_time` was not set).
   - As designed, unauthenticated removal does not lock the workstation. The user saw no lock event because the application had never entered the `AUTHORIZED` state.

---

### Root Cause 2: Lack of Synchronization / Thread Race Condition in `USBMonitor`

#### Code Inspection
In [`core/usb_monitor.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/core/usb_monitor.py):
- `_monitor_loop()` ran on background thread `USBMonitorThread`, calling `self._check_devices()` every 1.0 second.
- `MainWindow.nativeEvent()` intercepted Windows OS `WM_DEVICECHANGE` (`DBT_DEVICEREMOVECOMPLETE`) and immediately called `self.monitor.trigger_instant_check()`, which also called `self._check_devices()` on the **Main GUI Thread**.
- `_check_devices()` had **no mutual exclusion lock**.
- When a physical removal occurred, both threads could execute `_check_devices()` concurrently:
  - Thread 1 (GUI) reads `self._registered_usb_present = True`, sets `self._registered_usb_present = False`.
  - Thread 2 (Monitor) reads `self._registered_usb_present = False` concurrently, before `_removal_start_time` is updated or before state transitions complete.
  - Shared mutable state (`_registered_usb_present`, `_removal_start_time`, `_known_drive_letters`, `_last_logged_unknown`) was exposed to unsynchronized race conditions.

---

### Root Cause 3: GUI State Reflection Gaps for `WORKSTATION_LOCKED`

#### Code Inspection
1. In [`app/main_window.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/app/main_window.py#L260-L272):
   ```python
   if state.is_authenticated:
       self.lbl_sidebar_status.setText("● System Secured")
   elif state.protection_active:
       self.lbl_sidebar_status.setText("● Grace Countdown")
   else:
       self.lbl_sidebar_status.setText("● Standby")
       self.status_bar.showMessage("USB Guardian standing by. Insert registered physical token.")
   ```
   When the session transitioned to `SessionStatus.WORKSTATION_LOCKED`, `is_authenticated` was `False` and `protection_active` was `False`. The handler dropped into `else:`, erroneously resetting the sidebar status to **"● Standby"** instead of **"● Workstation Locked"**!
2. In [`app/dashboard.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/app/dashboard.py#L254-L270):
   The alert banner logic lacked an explicit branch for `WORKSTATION_LOCKED`, dropping into the default branch:
   `"● USB Guardian is standing by. Insert registered physical token to authorize."`
3. In [`app/authentication_view.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/app/authentication_view.py#L190-L201):
   There was no explicit UI messaging indicating that the workstation was locked due to USB removal, leaving the user without clear feedback.

---

### Root Cause 4: Path Coercion Gap in `KeyManager`

In [`core/key_manager.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/core/key_manager.py#L34):
`self.storage_dir = storage_dir or get_default_storage_dir()`
When callers passed `storage_dir` as a string (`str`), `secure_storage.write_laptop_public_key(self.storage_dir, ...)` failed with:
`TypeError: unsupported operand type(s) for /: 'str' and 'str'`
because `storage_dir` was expected to be a `pathlib.Path` instance.

---

## 3. Summary of Failure Chain

```
[Acceptance Test Run without DB Isolation]
       ↓
[Production DB Active Device Revoked; Dummy Token 15 Inserted as ACTIVE]
       ↓
[User Inserts Physical HP v232w Token (UUID ca5255a2...)]
       ↓
[App Searches for Token UUID aa900280... → Mismatch]
       ↓
[UI Reports "Device status: DISCONNECTED", "Standby"]
       ↓
[User Cannot Authenticate (Button Disabled; Session Remains Unauthenticated)]
       ↓
[User Unplugs USB]
       ↓
[Monitor Evaluates was_authenticated == False]
       ↓
[Grace Period NOT Started; Session Lock NOT Triggered]
```

---

## 4. Resolution Plan

1. **Restore Production Database Active Token:** Restore device ID 1 (`ca5255a2-a46b-439d-b94a-6a27eef093b8`, `v232w Token`, serial `4238B45B`, status `ACTIVE`) and restore the matching public key to `%LOCALAPPDATA%\USBGuardian\keys\registered_public_key.pem`.
2. **Isolate Acceptance Tests:** Modify `acceptance_test_rc1.py` to strictly execute inside temporary isolated directories (`tempfile.mkdtemp()`) so live database and key stores are never touched.
3. **Add Reentrant Scan Lock to `USBMonitor`:** Add `self._scan_lock = threading.RLock()` to synchronize `_check_devices()` between GUI events and background polling.
4. **Fix GUI State Reflection:** Add explicit handling for `SessionStatus.WORKSTATION_LOCKED` and `SessionStatus.GRACE_PERIOD_ACTIVE` across `MainWindow`, `DashboardView`, and `AuthenticationView`.
5. **Normalize `storage_dir`:** Coerce `storage_dir = Path(storage_dir)` in `KeyManager.__init__`.
6. **Automated Pipeline Verification:** Implement a comprehensive 11-step event pipeline test suite to verify end-to-end functionality and prevent regression.

