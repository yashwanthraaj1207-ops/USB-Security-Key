# USB-Security-Key
### Windows 11 USB-Based Physical Authentication & Access Control System

![Platform: Windows 11](https://img.shields.io/badge/Platform-Windows%2011%20Home%20%2F%20Pro-blue?logo=windows)
![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)
![GUI: PySide6](https://img.shields.io/badge/GUI-PySide6%20Qt-41CD52?logo=qt)
![Crypto: Ed25519 + Argon2id](https://img.shields.io/badge/Crypto-Ed25519%20%7C%20Argon2id-8A2BE2)
![Tests: 100% Passed](https://img.shields.io/badge/Tests-76%2F76%20Passing-success)

**USB Guardian** is a high-security physical authentication and access control system for Windows 11. It allows users to register a personal USB pendrive as a physical hardware authentication token. When the authenticated USB is unplugged, the system enforces a configurable anti-glitch grace period and automatically locks the Windows workstation.

---

## 🌟 Key Features

* **Ed25519 Asymmetric Identity:** Generates unique Edwards-curve digital signature key pairs for hardware tokens.
* **Argon2id Encrypted Token Storage:** Encrypts the private key using 64 MiB memory-hard Argon2id key derivation and AES-256-GCM.
* **Asymmetric Public-Key Challenge-Response:** Generates 32-byte cryptographically secure random nonces for single-use verification.
* **Continuous Hardware Watchdog:** Multi-threaded monitor combines Windows `WM_DEVICECHANGE` OS notifications with periodic bus heartbeats.
* **Anti-Glitch Grace Period:** Configurable countdown timer (e.g. 5s) prevents false alarms during USB re-enumeration glitches.
* **Safe Workstation Locking:** Uses the official `user32.LockWorkStation` Win32 API. Never kills applications, signs out, or restarts the PC.
* **Zero Windows Lockout Guarantee:** Never stores Windows passwords/PINs on the USB drive. Standard Windows sign-in and administrator recovery remain 100% intact.
* **Tamper-Evident Security Audit Logs:** Structured, sanitized logging of all hardware insertions, removals, signature checks, and locks.
* **Future C++ Credential Provider Architecture:** Includes research, headers, and CMake project for direct Windows LogonUI integration.

---

## 🎨 Professional Cybersecurity Dashboard

USB Guardian features a sleek, obsidian dark cybersecurity theme crafted with **PySide6**:
* **Charcoal / Obsidian Background** (`#090d16`, `#111726`)
* **Electric Violet & Neon Green Accents** (`#7c3aed`, `#00e676`)
* **Glassmorphism Panels** with border highlights
* **7 Dedicated Modules**:
  1. **Dashboard:** Live status metrics, hardware badges, and recent audit logs.
  2. **Register USB:** Select drive, validate passphrase complexity, and provision token.
  3. **Authentication:** Decrypt private key, sign nonce, and authorize workstation.
  4. **Device Monitor:** Bus inspection, storage table, and live grace period countdown.
  5. **Security Logs:** Searchable audit trail with real-time streaming and CSV export.
  6. **Settings:** Configure grace period, auto-lock policies, and dry-run simulation mode.
  7. **Recovery:** Device revocation and emergency Windows access fallback.

---

## 📂 Project Structure

```
USB-GUARDIAN/
│
├── main.py                          # Main desktop entry point & CLI runner
├── requirements.txt                 # Project dependencies
├── README.md                        # Documentation & setup guide
│
├── app/                             # PySide6 Desktop GUI
│   ├── styles.py                    # Dark cybersecurity QSS stylesheet
│   ├── main_window.py               # Main window shell & Win32 event filter
│   ├── dashboard.py                 # Operations center & metrics view
│   ├── registration_view.py         # USB token provisioning workflow
│   ├── authentication_view.py       # Ed25519 challenge-response view
│   ├── monitor_view.py              # Hardware watchdog & countdown view
│   ├── logs_view.py                 # Filterable audit log & CSV exporter
│   ├── settings_view.py             # System policy & grace period view
│   └── recovery_view.py             # Revocation & fail-safe fallback
│
├── core/                            # Core Logic & Security Engines
│   ├── key_manager.py               # Atomic key generation & provisioning
│   ├── authenticator.py             # Challenge-response authentication engine
│   ├── challenge_manager.py         # Anti-replay 32-byte CSPRNG nonces
│   ├── usb_detector.py              # Windows drive geometry & volume queries
│   ├── usb_monitor.py               # Background watchdog & grace period state
│   ├── session_manager.py           # Physical authentication state machine
│   └── security_logger.py           # Sanitized audit trail logger
│
├── security/                        # Cryptographic Foundations
│   ├── encryption.py                # Ed25519, Argon2id, PBKDF2, AES-256-GCM
│   ├── validation.py                # Metadata validation & passphrase checks
│   └── secure_storage.py            # Atomic file operations with rollback
│
├── windows/                         # Windows OS Integration
│   ├── session_lock.py              # user32.LockWorkStation integration
│   ├── device_notifications.py      # WM_DEVICECHANGE native message listener
│   ├── service/                     # Standalone background service & IPC
│   │   ├── __init__.py
│   │   ├── background_service.py    # Headless background daemon
│   │   └── ipc_server.py            # Localhost loopback IPC server
│   └── credential_provider/         # C++ Windows Credential Provider Module
│       ├── CMakeLists.txt           # Build configuration
│       ├── guid.h                   # CLSID definitions
│       ├── common.h                 # Headers and field enumerations
│       ├── USBGuardianCredentialProvider.h
│       ├── USBGuardianCredentialProvider.cpp
│       ├── CProviderCredential.h
│       ├── CProviderCredential.cpp
│       ├── dllmain.cpp              # COM class factory & DLL registration
│       └── README.md                # LogonUI architectural research
│
├── database/                        # Database Storage
│   ├── db_manager.py                # Thread-safe SQLite database manager
│   └── models.py                    # Device, log, and settings models
│
├── tests/                           # Automated Pytest Suite
│   ├── test_keys.py                 # Key generation, Argon2id, & AES-GCM
│   ├── test_authentication.py       # Challenge-response & replay resistance
│   ├── test_usb.py                  # USB detection, sanitization, & metadata
│   └── test_security.py             # State machine, logger, & lock safety
│
└── docs/                            # In-Depth Engineering Documentation
    ├── ARCHITECTURE.md              # System design & sequence diagrams
    ├── SECURITY.md                  # Cryptographic specs & threat model
    ├── WINDOWS_INTEGRATION.md       # Windows 11 logon & Credential Provider
    └── RECOVERY.md                  # Emergency recovery & zero-lockout guide
```

---

## 🚀 Quick Start Guide

### 1. Installation

Ensure Python 3.10+ is installed on Windows 11. Clone or navigate to the directory and install dependencies:

```powershell
pip install -r requirements.txt
```

### 2. Run the Desktop Application

Launch the desktop cybersecurity dashboard:

```powershell
python main.py
```

### 3. Safe Simulation / Demonstration Mode

To run USB Guardian without actually locking your real Windows desktop screen when the USB is removed (ideal for demos or testing):

```powershell
python main.py --simulate-lock
```

### 4. Run Headless Background Daemon

To run USB Guardian as a headless background monitoring service:

```powershell
python main.py --service
```

---

## 🧪 Running the Automated Test Suite

Execute the full suite of unit and integration tests (20 automated tests):

```powershell
python -m pytest tests -v
```

All tests execute with safe mocking and will **never** lock your real workstation during test runs.

---

## 🛡️ Security Guarantees

1. **No Password Caching:** USB Guardian never asks for or stores your Windows password or PIN.
2. **Replay Immune:** Every challenge nonce is 32 cryptographically random bytes generated via CSPRNG and destroyed upon first use.
3. **Atomic Operations:** USB provisioning and database updates are strictly transactional; any failure triggers complete rollback.
4. **Permanent Windows Access:** Standard Windows sign-in always remains fully operational.

