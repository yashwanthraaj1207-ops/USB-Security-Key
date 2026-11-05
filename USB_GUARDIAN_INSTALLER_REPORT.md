# USB Guardian — Windows Installer Report

**Project**: USB Guardian  
**Target Platform**: Microsoft Windows 11 / 10 AMD64 (x64)  
**Installer Binary**: [`dist/installer/USBGuardian_Setup.exe`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/dist/installer/USBGuardian_Setup.exe)  
**Installer Tool**: Inno Setup 6.7.3 Command-Line Compiler (`ISCC.exe`)  
**Installer Script**: [`packaging/installer.iss`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/packaging/installer.iss)  
**Build Status**: **SUCCESSFUL & VALIDATED**  

---

## 1. Executive Summary

A native, standalone Windows installer named **`USBGuardian_Setup.exe`** ($33.72\text{ MB}$, LZMA2 ultra compression) has been compiled. The installer packages the complete standalone distribution (`dist/USB Guardian/`) and manages administrative deployment, system shortcuts, desktop integration, safe upgrades, and non-destructive uninstallation.

---

## 2. Installer Specifications & Binary Metrics

| Parameter | Specification | Notes |
| :--- | :--- | :--- |
| **Installer File Name** | `USBGuardian_Setup.exe` | Stored in `dist/installer/` |
| **Output File Size** | **35,361,241 bytes** (~$33.72\text{ MB}$) | High-ratio solid LZMA2 compression |
| **Target Architecture** | `x64compatible` | 64-bit native Windows executable |
| **Default Installation Directory** | `C:\Program Files\USB Guardian\` | Standard Windows 64-bit program directory (`{autopf}`) |
| **Elevation Level** | `PrivilegesRequired=admin` | Standard UAC prompt for system-wide software deployment |
| **Setup Application Icon** | [`assets/icons/app_icon.ico`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/assets/icons/app_icon.ico) | Multi-resolution security shield icon |
| **Uninstaller** | `{app}\unins000.exe` | Registered in Windows "Installed Apps" / Control Panel |

---

## 3. Shortcut & System Integration

The installer automatically configures:
1. **Start Menu Shortcut**:
   - Location: `{autoprograms}\USB Guardian.lnk`
   - Target: `{app}\USB Guardian.exe`
   - Icon: `{app}\_internal\assets\icons\app_icon.ico`
2. **Desktop Shortcut** (Optional task):
   - Location: `{autodesktop}\USB Guardian.lnk`
3. **Automatic Startup** (Optional task):
   - Registry Key: `HKLM\Software\Microsoft\Windows\CurrentVersion\Run\USBGuardian`
   - Parameter: `"{app}\USB Guardian.exe" --simulate-lock` (Enforces simulation mode on automatic boot)

---

## 4. Upgrade & Data Preservation Architecture

### Critical Preservation Principle
The installer separates application code from user data:
- **Code & Binaries**: Stored in `C:\Program Files\USB Guardian\` (overwritten during upgrades).
- **Persistent Data**: Stored in `%LOCALAPPDATA%\USBGuardian\` (never overwritten during upgrades).

### Safe Upgrade Workflow
1. When a new version of `USBGuardian_Setup.exe` is executed, Inno Setup matches the unique GUID:
   `AppId={{D37E84B1-23B1-4A59-86BC-5FD011388E91}`.
2. The installer requests running instances to close gracefully via Windows Restart Manager.
3. Updated binaries and assets are installed into `C:\Program Files\USB Guardian\`.
4. The local SQLite database (`%LOCALAPPDATA%\USBGuardian\database\usb_guardian.db`), registered device identities, and HMAC audit chaining keys are left completely untouched.
5. On the first launch after upgrade, [`DatabaseManager.init_db()`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/database/db_manager.py#L33) automatically migrates any schema updates without data loss.

---

## 5. Non-Destructive Uninstallation Safety Hook

To prevent catastrophic accidental data loss (such as deleting audit histories or device identities), the uninstallation process is safeguarded by an explicit Pascal callback hook in `installer.iss`:

```pascal
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  DataDir: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    DataDir := ExpandConstant('{localappdata}\USBGuardian');
    if DirExists(DataDir) then
    begin
      if MsgBox('Do you want to completely erase your USB Guardian audit history and registered device identities?' + #13#10 + #13#10 +
                'Select NO if you plan to reinstall or upgrade later.' + #13#10 +
                'Select YES to permanently delete all local database records.',
                mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDYES then
      begin
        DelTree(DataDir, True, True, True);
      end;
    end;
  end;
end;
```

- **Default Button**: `MB_DEFBUTTON2` (defaults to **NO** if user presses Enter).
- **Safety Guarantee**: Uninstallation **never silently deletes** user data. User data is only purged if the user consciously selects YES.

