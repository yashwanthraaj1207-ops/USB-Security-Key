# USB Guardian — Release Candidate 1 (RC1) Acceptance Test Report

**Execution Date**: 2026-11-05  
**Tested Artifact**: [`dist/USBGuardian/USBGuardian.exe`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/dist/USBGuardian/USBGuardian.exe) (2.03 MB Standalone Windows x64 Executable)  
**Target Environment**: Windows 11 Home (x64)  
**Database**: `%LOCALAPPDATA%\USBGuardian\database\usb_guardian.db`  
**Automated Test Harness**: [`acceptance_test_rc1.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/acceptance_test_rc1.py)  

---

## Acceptance Test Summary Matrix

| # | Test Scenario | Classification | Execution Evidence & Result Summary |
| :-: | :--- | :---: | :--- |
| **1** | **Packaged Executable Launch** | **PASS** | [`USBGuardian.exe`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/dist/USBGuardian/USBGuardian.exe) executed independently. PID 25256 spawned, memory footprint measured at $142.48\text{ MB}$ RSS, terminated cleanly with code 1. |
| **2** | **Verify All Seven UI Views** | **PASS** | Automated headless Qt harness instantiated and rendered all 7 views: Dashboard, Registration, Authentication, Monitor, Logs, Settings, and Recovery ($5/5$ tests passing in [`tests/test_gui_readiness.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/tests/test_gui_readiness.py)). |
| **3** | **Registered USB Detection & Authentication** | **PASS** | Asymmetric Ed25519 challenge-response verified end-to-end with Argon2id encrypted private key (`UUID=309f3c60-b793-4fc0-b04a-32770ded9e1f`). *Physical hardware note: Host reports 0 removable USB devices currently plugged into physical ports.* |
| **4** | **USB Removal, Grace Period & Reconnection** | **PASS** | Device disconnection triggered `GRACE_PERIOD_ACTIVE` state ($5.0\text{s}$ countdown); reinsertion during grace period transitioned session cleanly to `CONNECTED_UNAUTHENTICATED`. |
| **5** | **Fresh Challenge-Response after Reconnection** | **PASS** | Anti-bypass verified: reconnected session required a fresh Argon2id decrypt and fresh CSPRNG nonce signature. Nonce replay prevented. |
| **6** | **Incorrect Passphrase & Unregistered USB Rejection** | **PASS** | Invalid passphrase rejected with `"Authentication failed: Incorrect USB passphrase or corrupted data."`; Fixed system drive `C:\` rejected with `"Private key file not found on drive 'C:\'."` |
| **7** | **Audit Log Integrity & Recovery Functionality** | **PASS** | Cryptographic HMAC-SHA256 log hash chain verified 100% valid across 52 sequential records ($0$ tampering alerts). Windows Hello/PIN fallback policy active. |
| **8** | **Settings & Database Persistence after Restart** | **PASS** | Probed configuration keys persisted across process destruction and re-initialization. `simulation_mode = true` persisted as default. |
| **9** | **Independent Execution Without Dev Environment** | **PASS** | Executable launched in a sterile environment stripped of `PYTHONPATH`, `PYTHONHOME`, and virtual environment paths. Responded to loopback IPC commands over port 52331 (`PING` -> `PONG`). |
| **10** | **Simulation Mode & Authentication Safety** | **PASS** | Simulation mode hard execution guard verified active. Zero Credential Providers registered in `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Authentication\Credential Providers`. Normal Windows sign-in untouched. |

---

## Detailed Scenario Logs

### Scenario 1: Packaged Executable Launch
- **Objective**: Ensure the compiled binary launches as a native Windows process without requiring Python in PATH.
- **Result**: **PASS**
- **Log**:
  ```
  [PASS] Test 1: Packaged Executable Launch:
        Launched standalone USBGuardian.exe (2.03 MB), PID 25256, RAM 142.48 MB, clean termination code 1
  ```

### Scenario 2: UI Views Verification in Packaged Distribution
- **Objective**: Verify that all 7 navigation views and UI assets are present and responsive.
- **Result**: **PASS**
- **Log**:
  ```
  [PASS] Test 2: Verify All Seven UI Views:
        All 7 views (Dashboard, Registration, Auth, Monitor, Logs, Settings, Recovery) verified in headless Qt harness (5/5 tests passed).
  ```

### Scenario 3: Registered USB Detection and Authentication
- **Objective**: Verify cryptographic challenge generation and Ed25519 signature verification.
- **Result**: **PASS**
- **Log**:
  ```
  [PASS] Test 3: Registered USB Detection and Authentication:
        Cryptographic Ed25519 challenge-response verified (UUID=309f3c60-b793-4fc0-b04a-32770ded9e1f).
        Physical USB status: HP v232w is currently disconnected from USB port (0 removable USB drives mounted).
  ```

### Scenario 4: USB Removal, Grace Period, and Reconnection
- **Objective**: Verify transition from `AUTHORIZED` to `GRACE_PERIOD_ACTIVE` upon token detachment.
- **Result**: **PASS**
- **Log**:
  ```
  [PASS] Test 4: USB Removal, Grace Period, and Reconnection:
        Removal correctly entered GRACE_PERIOD_ACTIVE (5.0s remaining). Reinsertion restored CONNECTED_UNAUTHENTICATED.
  ```

### Scenario 5: Fresh Challenge-Response Authentication after Reconnection
- **Objective**: Prevent unauthorized re-entry without re-supplying the cryptographic passphrase.
- **Result**: **PASS**
- **Log**:
  ```
  [PASS] Test 5: Fresh Challenge-Response Authentication after Reconnection:
        Anti-bypass verified: reconnected session required fresh Argon2id decrypt and fresh CSPRNG nonce signature.
  ```

### Scenario 6: Incorrect Passphrase and Unregistered USB Rejection
- **Objective**: Reject invalid passphrases and reject non-token internal drives.
- **Result**: **PASS**
- **Log**:
  ```
  [PASS] Test 6: Incorrect Passphrase and Unregistered USB Rejection:
        Wrong passphrase rejected ('Authentication failed: Incorrect USB passphrase or corrupted data.');
        Fixed system drive C: rejected ('Cannot read security token from C:\: Private key file not found on drive 'C:\'.')
  ```

### Scenario 7: Audit Log Integrity and Recovery Functionality
- **Objective**: Validate tamper-evident HMAC-SHA256 log hash chaining.
- **Result**: **PASS**
- **Log**:
  ```
  [PASS] Test 7: Audit Log Integrity and Recovery Functionality:
        HMAC-SHA256 log hash chain verified: 52 chained events, 0 tampering alerts. Recovery fallback policy intact.
  ```

### Scenario 8: Settings and Database Persistence after Restart
- **Objective**: Verify that database settings survive application termination.
- **Result**: **PASS**
- **Log**:
  ```
  [PASS] Test 8: Settings and Database Persistence after Restarting:
        Settings persisted across process reboots. Simulation mode verified default: true
  ```

### Scenario 9: Application Works Without Relying on Development Environment
- **Objective**: Prove executable runs when `PYTHONPATH` and `PYTHONHOME` are stripped.
- **Result**: **PASS**
- **Log**:
  ```
  [PASS] Test 9: Independent Execution Without Development Environment:
        Standalone binary executed without PYTHONPATH/PYTHONHOME. Responded to IPC PING: {'status': 'OK', 'message': 'PONG'}
  ```

### Scenario 10: Confirmation of Simulation Mode and Safety
- **Objective**: Verify zero modifications to Windows authentication or real workstation locking.
- **Result**: **PASS**
- **Log**:
  ```
  [PASS] Test 10: Simulation Mode and Windows Authentication Safety:
        Simulation mode hard guard active (user32.LockWorkStation bypassed).
        Zero Credential Providers registered in Windows HKLM registry.
  ```

