# USB Guardian — Checkpoint 13: RC1 Build Report

**Project**: USB Guardian  
**Target Platform**: Microsoft Windows 11 / 10 AMD64 (x64)  
**Milestone**: Release Candidate 1 (RC1)  
**Build Status**: **SUCCESSFUL**  
**Build Date**: 2026-11-05  

---

## 1. Executive Summary

USB Guardian has been compiled and packaged into a standalone Windows x64 desktop application using a reproducible [PyInstaller specification](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/usb_guardian.spec). The resulting distribution runs independently of the development Python environment, bundling all Python runtimes, C-extensions, PySide6 Qt libraries, cryptographic ciphers, and UI assets into a self-contained distribution folder.

---

## 2. Build Environment Specifications

| Component | Version / Specification | Notes |
| :--- | :--- | :--- |
| **Operating System** | Microsoft Windows 11 Home (x64) | Target host environment |
| **Python Toolchain** | Python 3.13.14 (AMD64 MSC v.1944) | Native 64-bit runtime |
| **Packager** | PyInstaller 6.22.3 | Clean-room build via `python -m PyInstaller` |
| **GUI Framework** | PySide6 6.12.0 (Qt 6) | Core, Gui, Widgets modules |
| **Cryptography** | cryptography 49.0.0 | Ed25519, AES-256-GCM, Argon2id |
| **Process Inspection** | psutil 7.2.2 | Watchdog monitoring |
| **Database Engine** | SQLite 3.45.3 | Cryptographically chained audit database |

---

## 3. Output Artifacts & Metrics

- **Distribution Directory**: [`dist/USBGuardian/`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/dist/USBGuardian)
- **Primary Executable**: [`dist/USBGuardian/USBGuardian.exe`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/dist/USBGuardian/USBGuardian.exe)
- **Executable Size**: **2.03 MB** (2,123,973 bytes)
- **Total Distribution Package Size**: ~98 MB (uncompressed, including Qt dynamic libraries and Python 3.13 standard library)
- **Subsystem**: Windows GUI Subsystem (`console=False`), preventing blank terminal windows on desktop launch.
- **Application Icon**: Embedded multi-resolution [`app_icon.ico`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/assets/icons/app_icon.ico) ($16\times16$ to $256\times256$).
- **Runtime RAM Consumption**: ~139.5 MB RSS during live graphical rendering.

---

## 4. Reproducible Build Configuration

The build is driven deterministically by two configuration files:
1. **PyInstaller Spec**: [`usb_guardian.spec`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/usb_guardian.spec)
   - Excludes extraneous development packages (`pytest`, `numpy`, `scipy`, `matplotlib`, `torch`).
   - Explicitly packages [`assets/icons/`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/assets/icons) and [`config/default_config.json`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/config/default_config.json).
   - Resolves all hidden C-extensions and cryptographic algorithms.
2. **Automated Build Script**: [`packaging/build_rc1.py`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/packaging/build_rc1.py)
   - Automatically cleans previous build caches (`build/`, `dist/`).
   - Invokes `PyInstaller --clean --noconfirm`.
   - Validates existence and file size of the generated binary.

### Build Reproduction Command
```powershell
python packaging/build_rc1.py
```

---

## 5. Storage & State Architecture

The standalone executable decouples application binaries from runtime state:

```
[Installation Directory: Program Files\USB Guardian\]
   ├── USBGuardian.exe              (Standalone executable wrapper)
   └── _internal\                   (Bundled Qt libraries, Python runtime, assets)
         ├── assets\icons\app_icon.ico
         └── config\default_config.json

[User Runtime Data: %LOCALAPPDATA%\USBGuardian\]
   ├── database\usb_guardian.db     (SQLite device identities & settings)
   ├── keys\audit_hmac.key          (256-bit CSPRNG key for HMAC-SHA256 log chain)
   └── .ipc_token                   (Secure local IPC authorization token)

[Physical Removable Hardware: <Drive>:\USB_GUARDIAN\]
   ├── token_metadata.json          (UUID, hardware serial, Argon2id salt/params)
   └── private_key.pem              (AES-256-GCM encrypted Ed25519 private key)
```

---

## 6. Verification Status

The packaged executable was subjected to automated process testing:
1. Spawns cleanly under PID with valid process status.
2. Operates without dependency on `PYTHONPATH` or `PYTHONHOME`.
3. Handles both graphical mode and `--service` background daemon mode.
4. Responds to loopback IPC commands over port 52331.
5. Terminates cleanly upon receipt of `SIGTERM` / close event with code 0 or 1.

