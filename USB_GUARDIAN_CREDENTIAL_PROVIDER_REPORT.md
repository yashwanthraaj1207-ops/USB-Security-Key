# USB Guardian — Native C++ Credential Provider Audit Report

**Component**: Pre-Login Windows Sign-In Integration  
**Source Directory**: [`windows/credential_provider/`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/windows/credential_provider)  
**CLSID**: `{2D762D71-118E-4A42-9988-10A0A58449D2}`  
**Status**: **SOURCE AUDITED & VALIDATED (Compilation & Registration Staged for VM)**  

---

## 1. Source Code Inventory & COM Interface Compliance

| Source File | Role & COM Interfaces | Audit Findings |
| :--- | :--- | :--- |
| [`guid.h`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/windows/credential_provider/guid.h) | Provider CLSID Definition | Standard `DEFINE_GUID` macro for `{2D762D71-118E-4A42-9988-10A0A58449D2}`. |
| [`common.h`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/windows/credential_provider/common.h) | Win32 / SDK Header Definitions | Defines `USB_PROVIDER_FIELD_ID` enum (`TITLE`, `STATUS`, `PASSPHRASE`, `WIN_PASSWORD`, `SUBMIT_BUTTON`). |
| [`dllmain.cpp`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/windows/credential_provider/dllmain.cpp) | In-Process COM Server Entry Points | Implements `DllGetClassObject`, `DllCanUnloadNow`, `DllRegisterServer`, `DllUnregisterServer` with thread-safe `_cRef` tracking. |
| [`USBGuardianCredentialProvider.h/cpp`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/windows/credential_provider/USBGuardianCredentialProvider.h) | Provider Architecture | Implements `ICredentialProvider` and `ICredentialProviderSetUserArray`. Filters usage scenarios to `CPUS_LOGON` and `CPUS_UNLOCK_WORKSTATION`. |
| [`CProviderCredential.h/cpp`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/windows/credential_provider/CProviderCredential.h) | Credential Tile UI & Serialization | Implements `ICredentialProviderCredential` and `ICredentialProviderCredential2`. Manages field descriptors, strings, and command clicks. |

---

## 2. Memory Ownership & Serialization Contract

Under the Windows Credential Provider architecture, memory ownership is strictly defined:
- Any buffer returned through `GetSerialization` in `CREDENTIAL_PROVIDER_CREDENTIAL_SERIALIZATION.rgbSerialization` **must** be allocated using `CoTaskMemAlloc()`.
- Windows `LogonUI.exe` takes full ownership of the buffer and frees it via `CoTaskMemFree()`.
- [`CProviderCredential.cpp`](file:///c:/Users/Yashw/OneDrive/Desktop/Project Workspace/Project Workspace/Project/Pendrive/windows/credential_provider/CProviderCredential.cpp) allocates exactly:
  $$\text{cbTotal} = \text{sizeof}(\text{MSV1\_0\_INTERACTIVE\_LOGON}) + \text{cbDomain} + 2 + \text{cbUser} + 2 + \text{cbPass} + 2$$
  using `CoTaskMemAlloc()`, zeroes the memory via `ZeroMemory()`, and packs UNICODE_STRING descriptors with relative data offsets.

---

## 3. Credential Serialization vs Actual Authentication

> [!IMPORTANT]
> **A Credential Provider does NOT authenticate credentials. It serializes them for LSA.**

- In Windows 11 Home local accounts, authentication is performed exclusively by the Local Security Authority Subsystem (`LSASS.exe`) invoking the `msv1_0.dll` authentication package against the Security Account Manager (`SAM`) database.
- An Ed25519 digital signature cannot directly satisfy an `MSV1_0_INTERACTIVE_LOGON` request because Windows local accounts authenticate exclusively using NTLM password hashes ($MD4(\text{UTF-16LE}(Password))$).
- **Two-Factor Authentication (2FA) Architecture**:
  1. **Factor 1 (What You Have)**: Physical HP v232w USB token containing Argon2id-encrypted private key + successful Ed25519 challenge-response signature.
  2. **Factor 2 (What You Know)**: User enters their Windows local account password into the tile.
  3. If Factor 1 fails (wrong passphrase, missing USB, spoofed hardware), the tile blocks serialization entirely.
  4. Only when both factors pass does the provider serialize `MSV1_0_INTERACTIVE_LOGON` for LogonUI.

---

## 4. Host Environment & Compiler Prerequisites

- **Required Compiler**: 64-bit Microsoft Visual C++ (`cl.exe` MSC v1940+) and Windows 11 SDK (`credentialprovider.h`, `ntsecapi.h`).
- **Host Status**: The current host machine has MinGW 32-bit GCC, but lacks 64-bit MSVC Build Tools.
- **Safety Staging**: Compilation must be performed on a dedicated machine or CI runner equipped with Visual Studio 2022 Build Tools (Desktop C++ workload).

---

## 5. Strict Safety Compliance Confirmation

- **Zero Registry Modification**: No keys written to `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Authentication\Credential Providers`.
- **Primary Laptop Untouched**: DLL is not registered on the primary operating system.
- **VM Testing Protocol**: Live pre-login testing must be conducted inside a Hyper-V / VMware Windows 11 staging VM with a snapshot rollback point to prevent lockout.

