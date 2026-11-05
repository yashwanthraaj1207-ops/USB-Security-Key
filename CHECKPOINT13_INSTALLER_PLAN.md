# USB Guardian — Checkpoint 13: Windows Installer Plan

**Component**: Windows Deployment & Installation  
**Target Solution**: Inno Setup 6 (x64)  
**Configuration Script**: [`packaging/installer.iss`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/packaging/installer.iss)  

---

## 1. Installer Solution Evaluation

| Criterion | Inno Setup 6 [Selected] | NSIS | WiX Toolset (MSI) |
| :--- | :--- | :--- | :--- |
| **Reliability on Windows 11** | Industry standard, robust rollback, clean x64 handling | High | High |
| **Scripting Complexity** | Declarative INI-style syntax with Pascal Scripting | Complex low-level macro scripting | Extremely complex XML schemas |
| **Uninstall Data Preservation** | Clean custom hooks via `CurUninstallStepChanged` | Requires custom plugin hooks | Difficult custom actions |
| **Binary Footprint** | Ultra-efficient LZMA2 compression (~32 MB compressed) | Compact | Moderate to large |
| **Elevation Handling** | Native `PrivilegesRequired=admin` | Requires UAC plugins | Native |

**Conclusion**: **Inno Setup 6** is the optimal installer tool for USB Guardian, providing clean administrative installation, desktop and Start Menu shortcut generation, uninstaller registration in Windows "Installed Apps", and explicit user-prompted data preservation.

---

## 2. Directory Layout & Shortcuts

### Installation Target
- **Default Directory**: `C:\Program Files\USB Guardian\` (`{autopf}\USB Guardian`)
- **Per-User Alternative**: `%LOCALAPPDATA%\Programs\USB Guardian\`

### Start Menu & Desktop Shortcuts
- **Start Menu**: `{autoprograms}\USB Guardian.lnk` pointing to `{app}\USBGuardian.exe` with embedded icon `{app}\_internal\assets\icons\app_icon.ico`.
- **Desktop Shortcut** (Optional user checkbox): `{autodesktop}\USB Guardian.lnk`.
- **Startup Autorun** (Optional user checkbox): Adds Windows Run key `HKLM\Software\Microsoft\Windows\CurrentVersion\Run\USBGuardian` pointing to `"{app}\USBGuardian.exe" --simulate-lock`.

---

## 3. Data Preservation & Uninstallation Policy

### Critical Security Rule
> [!IMPORTANT]
> **Never delete user cryptographic tokens, registered device records, or security audit logs during ordinary uninstallation without explicit, conscious user consent.**

### Uninstallation Workflow
1. The Windows Control Panel / Settings app invokes `{app}\unins000.exe`.
2. All application binaries, dynamic libraries, and assets inside `C:\Program Files\USB Guardian\` are removed.
3. Start Menu and Desktop shortcuts are unlinked.
4. **Data Preservation Hook**:
   The installer executes Pascal hook `CurUninstallStepChanged(usPostUninstall)`:
   - Detects whether `%LOCALAPPDATA%\USBGuardian\` exists.
   - Prompts the user with an explicit dialog:
     > *"Do you want to completely erase your USB Guardian audit history and registered device identities? Select NO if you plan to reinstall or upgrade later. Select YES to permanently delete all local database records."*
   - If user selects **NO**: `%LOCALAPPDATA%\USBGuardian\` (database, HMAC key, configuration) remains intact.
   - If user selects **YES**: The directory is purged.

---

## 4. Safe Upgrade Procedure

When a new version (e.g., `v1.0.0-rc2` or `v1.0.0`) is released:
1. The new installer detects the existing `AppId={{D37E84B1-23B1-4A59-86BC-5FD011388E91}`.
2. It stops running `USBGuardian.exe` processes via Windows restart manager.
3. It overwrites binaries in `C:\Program Files\USB Guardian\` with the updated versions.
4. `%LOCALAPPDATA%\USBGuardian\database\usb_guardian.db` is left completely untouched.
5. On the first launch of the updated application, [`DatabaseManager.init_db()`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/database/db_manager.py#L33) performs any required schema migrations while preserving all existing audit records and cryptographic tokens.

