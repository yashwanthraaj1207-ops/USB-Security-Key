# USB Guardian — Release Candidate 1 (RC1) Known Issues

**Document Version**: 1.0.0-rc1  
**Status**: Active Staging Audit  

---

## 1. Classification of Known Issues

| ID | Issue Description | Impact | Workaround / Mitigation | Target Milestone |
| :-: | :--- | :--- | :--- | :---: |
| **ISS-01** | **Physical HP v232w Token Disconnected from Host Port** | Live physical hardware detection reflects "offline" when the flash drive is physically unplugged. | Reconnect the physical HP v232w flash drive to an available USB port prior to manual end-user GUI testing. | Operational |
| **ISS-02** | **Windows SmartScreen "Unknown Publisher" Notice** | Packaged executable is not signed with a Microsoft Authenticode EV code-signing certificate. | For manual testing, click "More info" -> "Run anyway" in the Windows SmartScreen prompt. Production build requires an EV code signing certificate. | Post-RC1 |
| **ISS-03** | **Pre-Login Credential Provider Uncompiled** | The C++ Credential Provider DLL source in `windows/credential_provider/` is audited but not yet compiled into binary DLL form due to missing MSVC build tools. | Pre-login authentication remains deferred; continuous desktop workstation presence protection is 100% active. | v2.0 |
| **ISS-04** | **Commodity USB Flash Drive Emulation Attack Vector** | Standard USB mass storage controller serials can be emulated by specialized physical microcontrollers (e.g. Facedancer/Pico). | Argon2id passphrase encryption prevents private key extraction from stolen drives; for enterprise zero-trust hardware protection, transition to smartcards/FIDO2 tokens. | Architecture |
| **ISS-05** | **Windowed Executable Console Suppression** | Running `USBGuardian.exe --help` from PowerShell produces no stdout text in terminal. | Standard Windows GUI subsystem behavior (`console=False`); desktop users interact via the GUI, and daemon users inspect database logs or IPC responses. | By Design |

---

## 2. Verified Non-Issues & False Alerts

- **System Drive False Positives**: Fully resolved in Checkpoint 5. Drives `C:\` and `D:\` (NVMe internal storage) are classified as fixed internal disks via Win32 `IOCTL_STORAGE_QUERY_PROPERTY` and never misidentified as USB tokens.
- **Log Tampering**: Fully protected by HMAC-SHA256 hash chaining using a persistent 256-bit CSPRNG key in `%LOCALAPPDATA%\USBGuardian\keys\audit_hmac.key`.
- **Accidental Lockout**: Prevented by architecture; normal Windows sign-in (PIN, Password, Windows Hello) is untouched.

