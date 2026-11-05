# USB Guardian — Release Candidate 1 (RC1) Final Status

**Release**: USB Guardian Desktop Security Suite  
**Version**: 1.0.0-rc1  
**Build Target**: Windows 11 / 10 AMD64 (x64)  
**Binary Location**: [`dist/USBGuardian/USBGuardian.exe`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/dist/USBGuardian/USBGuardian.exe)  
**Readiness Level**: **RELEASE CANDIDATE 1 (Ready for Manual Verification & User Staging)**  

---

## 1. Product Status Overview

USB Guardian has successfully completed all packaging, code audit, concurrency hardening, and automated regression phases. 

- **Automated Test Suite**: **81 / 81 tests passing** ($0$ warnings, $0$ failures).
- **Formal Acceptance Testing**: **10 / 10 acceptance scenarios PASSED** on the packaged standalone binary.
- **Packaged Executable**: Produced via [reproducible PyInstaller spec](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/usb_guardian.spec) ($2.03\text{ MB}$ wrapper, ~$98\text{ MB}$ total distribution folder).
- **Installer Definition**: Complete [Inno Setup 6 script](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/packaging/installer.iss) with automated data preservation hooks.

---

## 2. Launch Instructions for Manual User Testing

To launch and manually test the packaged standalone application on Windows 11:

### Command (from Project Root)
```powershell
.\dist\USBGuardian\USBGuardian.exe --simulate-lock
```

### What to Expect on Launch
1. **Security Operations Center Dashboard**: Loads in dark cybersecurity theme with 4 live status cards (Registered Token, Hardware Connection, Authentication Status, Protection Status).
2. **Device Monitor View**: Real-time listing of attached storage hardware with bus-type classification (NVMe vs USB).
3. **Registration View**: Step-by-step form to provision a new physical USB token with Argon2id + AES-256-GCM encryption.
4. **Authentication View**: Challenge-response verification prompt.
5. **Activity Logs View**: Real-time table of HMAC-SHA256 chained security audit logs.
6. **Settings View**: Configurable removal grace period ($0-60\text{s}$), auto-lock toggles, and simulation mode switch.
7. **Recovery View**: Emergency fallback instructions and device revocation controls.

---

## 3. Critical Safety Compliance Confirmation

> [!IMPORTANT]
> - **Simulation Mode Enforced**: `simulation_mode = true` remains the persistent default in `%LOCALAPPDATA%\USBGuardian\database\usb_guardian.db`. Real Windows desktop locking (`user32.LockWorkStation`) is **never executed** unless the user explicitly toggles Simulation Mode off.
> - **Windows Login Security**: No Windows passwords, PINs, or SAM database hashes are stored or modified.
> - **Windows Registry Cleanliness**: Zero Credential Provider DLLs are registered in `HKLM`. Windows Hello, PIN, and local password sign-in remain 100% operational.
> - **Safe Uninstallation**: Ordinary uninstallation preserves user tokens and audit logs unless explicit confirmation is provided.

---

## 4. Production Readiness Disclaimer

While Release Candidate 1 is fully functional and stable for desktop continuous access control:
- **Production Readiness** for general public distribution requires an **EV Code Signing Certificate** to eliminate Windows SmartScreen warnings.
- **Pre-Login Integration** via the native C++ Credential Provider is deferred to v2.0 pending installation of Visual Studio Build Tools and VM staging.

