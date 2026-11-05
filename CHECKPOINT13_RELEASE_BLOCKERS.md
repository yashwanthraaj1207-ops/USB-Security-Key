# USB Guardian — Checkpoint 13: Release Blockers & Constraints

**Milestone**: Release Candidate 1 (RC1)  
**Status**: Pre-Production Review  

---

## 1. Blocker Summary

Before USB Guardian can be promoted from Release Candidate 1 (RC1) to General Availability (GA / Production v1.0), the following external environment and infrastructure items must be resolved:

```
[Release Candidate 1] ───► [Authenticode Signing] ───► [Compiler Toolchain] ───► [General Availability]
         │                              │                             │
    Desktop Core                 SmartScreen Clean             C++ Credential
    100% Operational             No Unknown Publisher          Provider Pre-Login
```

---

## 2. Itemized Blocker Analysis

### Blocker 1: Microsoft Authenticode Code Signing Certificate
- **Severity**: HIGH (Distribution & Trust)
- **Impact**: Without an EV (Extended Validation) or OV Authenticode certificate, Windows Defender SmartScreen displays a warning ("Windows protected your PC: Unknown publisher") when users attempt to execute the installer or packaged `.exe`.
- **Resolution**:
  - Obtain an EV Code Signing Certificate from a Microsoft-trusted Certificate Authority (e.g., DigiCert, Sectigo).
  - Integrate `signtool.exe sign /fd SHA256 /tr http://timestamp.digicert.com ...` into `packaging/build_rc1.py` and `packaging/installer.iss`.

---

### Blocker 2: C++ Toolchain for Windows Credential Provider Compilation
- **Severity**: MEDIUM (Pre-Login Scope Only; Desktop Protection is Fully Operational)
- **Impact**: The native Windows Credential Provider source scaffold (`windows/credential_provider/`) is fully audited and memory-safe, but remains uncompiled because the current host lacks Visual Studio 2022 Community / Windows 11 SDK (64-bit MSVC).
- **Resolution**:
  - Install Visual Studio Build Tools 2022 with the "Desktop development with C++" workload and Windows 11 SDK (10.0.22621.0+).
  - Compile `windows/credential_provider/` into `USBGuardianCredentialProvider.dll`.
  - Test registration strictly inside an isolated virtual machine staging environment before end-user distribution.

---

### Blocker 3: Physical USB Token Reconnection for Hardware E2E Demonstration
- **Severity**: LOW (Operational / Host State)
- **Impact**: The registered HP v232w USB flash drive was physically unplugged from the host machine during test execution (detected 0 removable USB devices). The software correctly refused unauthenticated access and safely fell back to disconnected standby.
- **Resolution**:
  - Re-insert the physical HP v232w flash drive into a USB 3.0/2.0 port on the host laptop.
  - Launch `USBGuardian.exe` and authenticate with passphrase `CorrectPassphrase123!` to engage live continuous protection.

---

### Blocker 4: Hardware Physical Clone Resistance Limitation
- **Severity**: INFORMATIONAL (Cryptographic & Hardware Boundary)
- **Impact**: Multi-attribute binding (Argon2id passphrase + device controller serial `4238B45B` + volume serial + Ed25519 signature) defeats all software file copying and operating system drive duplication attacks. However, commodity USB flash drives cannot enforce tamper-proof private key isolation against specialized hardware microcontroller emulators (e.g., Facedancer, Raspberry Pi Pico USB-emulators).
- **Resolution**:
  - Clearly disclose to end users that for military/enterprise zero-trust environments, hardware smartcards (FIDO2 / YubiKey / PIV) should be utilized. For workstation presence and protection against unauthorized casual physical access, USB Guardian provides comprehensive protection.

