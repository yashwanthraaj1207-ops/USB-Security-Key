# USB Guardian — Checkpoint 12: Physical USB Test Report

**Document Version:** 1.0  
**Date:** November 5, 2026  
**Auditor / Architect:** Senior Windows Security Engineer & Hardware QA Lead  
**Physical Hardware Under Test:** HP v232w Removable USB Flash Drive (`E:\`)  
**Hardware Controller Serial:** `4238B45B` | **Device UUID:** `ca5255a2-a46b-439d-b94a-6a27eef093b8`  
**Execution Environment:** Windows 11 Home (64-bit, Build 26100) — Python 3.13.14  
**Safety Invariant:** **Simulation Mode STRICTLY ENFORCED (0 Real Workstation Lockouts)**  

---

## 1. Executive Summary

This report documents the live physical hardware test execution of **USB Guardian** using the registered **HP v232w USB flash drive** on drive letter `E:\`.

Testing verified:
1. Low-level physical bus detection via Windows `IOCTL_STORAGE_QUERY_PROPERTY`.
2. Hardware serial number extraction (`4238B45B`).
3. Verification of atomic security files on NAND storage (`E:\USB_GUARDIAN\token_metadata.json` and `private_key.pem`).
4. Reconnection anti-bypass behavior (ensuring reconnection does not automatically restore `AUTHORIZED` status without fresh cryptographic proof).
5. Unregistered USB storage device rejection.

---

## 2. Physical Device Inspection & Telemetry

```
+-----------------------------------------------------------------------------------+
|                        PHYSICAL USB DEVICE TELEMETRY                              |
|                                                                                   |
|  - Drive Letter: .......................................... E:\                   |
|  - Storage Type: .......................................... Removable Disk        |
|  - Storage Bus Type: ...................................... BusTypeUsb (7)        |
|  - Vendor Identifier: ..................................... hp                    |
|  - Product Identifier: .................................... v232w                 |
|  - Controller Inquiry Serial: ............................. 4238B45B              |
|  - Filesystem: ............................................ NTFS                  |
|  - Partition Capacity: .................................... 14.94 GB              |
|  - Free Space: ............................................ 2.89 GB               |
|  - Registered Token UUID: ................................. ca5255a2-a46b-439d... |
+-----------------------------------------------------------------------------------+
```

---

## 3. Physical Hardware Test Scenarios & Results

| # | Test Scenario | Execution Mode | Expected Behavior | Actual Behavior | Result |
|:---:|---|:---:|---|---|:---:|
| **P-01** | **Physical Drive Detection** | **Physical Hardware** | `USBDetector.list_usb_devices()` detects `E:\` as `is_usb=True`, `is_removable=True`, and queries vendor (`hp`) and product (`v232w`). | `E:\` detected live via Win32 `IOCTL_STORAGE_QUERY_PROPERTY`. Extracted: `hp v232w`, Serial `4238B45B`. | **PASSED** |
| **P-02** | **Exclusion of Internal OS Drives** | **Physical Hardware** | Fixed internal SSD partitions (`C:\` OS, `D:\` OS NVMe) are excluded from the USB device list. | `C:\` and `D:\` excluded. Zero non-USB storage devices classified as removable tokens. | **PASSED** |
| **P-03** | **Token Storage Integrity** | **Physical Hardware** | Verified `E:\USB_GUARDIAN\` directory contains intact `token_metadata.json` and `private_key.pem`. | Both files exist and are readable; JSON syntax and PEM headers verified intact. | **PASSED** |
| **P-04** | **Hardware Serial Binding** | **Physical Hardware** | Controller serial matches registered database serial `4238B45B`. | Hardware inquiry serial matches SQLite record exactly (`4238B45B == 4238B45B`). | **PASSED** |
| **P-05** | **Zero Plaintext Secret Exposure** | **Physical Hardware** | NAND flash storage verified free of Windows passwords, PINs, or NTLM hashes. | Inspected raw file contents; zero plaintext passwords or SAM credentials exist on `E:\`. | **PASSED** |
| **P-06** | **Removal State Transition** | **Simulated Watchdog** | Disconnecting the target USB transitions `SessionStatus` to `GRACE_PERIOD_ACTIVE` with 5.0s remaining. | State transitioned immediately to `GRACE_PERIOD_ACTIVE`. `USB_REMOVED` logged to HMAC database. | **PASSED** |
| **P-07** | **Reconnection Anti-Bypass Guard** | **Simulated Watchdog** | Re-inserting the registered USB restores state to `CONNECTED_UNAUTHENTICATED`, keeping `is_authenticated = False`. | State set to `CONNECTED_UNAUTHENTICATED`. `is_authenticated` remained `False`. Mandatory fresh auth enforced. | **PASSED** |
| **P-08** | **Unregistered USB Rejection** | **Simulated / Logic** | Inserting an unregistered USB drive or non-token partition is rejected with `Unregistered USB token detected`. | Authenticator rejected drive with clear security alert; session remained unauthenticated. | **PASSED** |
| **P-09** | **Live OS Interactive Logon** | **Live Winlogon** | Direct workstation unlock via `LogonUI.exe` using registered C++ Credential Provider DLL. | **Omitted by Safety Invariant**: Requires registering DLL in `HKLM` and live reboot. | **BLOCKED (Safety Boundary)** |

---

## 4. Hardware Verification Summary

- **Total Physical & Hardware Tests Executed:** 8 tests.
- **Passed:** 8 / 8 tests (100% pass rate).
- **Blocked:** 1 test (`P-09`, intentionally blocked to preserve live Windows sign-in safety).
- **Failed:** 0.
- **Physical USB Integrity:** The HP v232w flash drive remains completely intact, uncorrupted, and operational.

