# USB Guardian — Checkpoint 12: UI / UX Audit & Usability Review

**Document Version:** 1.0  
**Date:** November 5, 2026  
**Auditor / Architect:** Senior UI/UX Designer & Windows Security Engineer  
**Frontend Framework:** PySide6 6.12.0 (Qt 6.8.0) — QSS Dark Theme  
**Target Desktop:** Windows 11 (High-DPI 100%–150% Scaling)  

---

## 1. Design Philosophy & Visual Language

USB Guardian employs a high-contrast **obsidian cybersecurity aesthetic**:
- **Background Tones:** Deep Charcoal (`#090d16`) and Dark Slate (`#111726`).
- **Accent Tones:** Electric Violet (`#7c3aed`), Neon Emerald (`#00e676`), and Warning Amber (`#ffab00`).
- **Typography:** Segoe UI Variable / Inter font stack with strict hierarchy.
- **Micro-Interactions:** Asynchronous progress indicators, subtle hover borders, and glowing status pills.

---

## 2. Comprehensive View-by-View Usability Audit

### View 1: Dashboard (`app/dashboard.py`)
- **Strengths:**
  - Hero status badge provides instantaneous visual feedback (`PROTECTED`, `GRACE PERIOD ACTIVE`, `LOCKED`).
  - Three primary quick-action cards ("Lock Workstation Now", "Authenticate Token", "Register Device") allow immediate single-click access.
  - Live activity feed shows the 5 most recent security events without leaving the main dashboard.
- **Usability Findings & Minor Flaws:**
  - *Observation:* On very small resolution screens ($<900\times 600$), the metrics grid requires vertical scrolling.
  - *Recommendation for V1.1:* Implement a responsive 2-column to 1-column layout reflow when the window width drops below 1000px.

### View 2: Registration View (`app/registration_view.py`)
- **Strengths:**
  - Dedicated background thread (`DriveScanWorker`) prevents GUI freezing while querying physical drive geometry.
  - Real-time passphrase strength meter (evaluating length, uppercase, numbers, and special characters) with a colored entropy bar.
  - Confirmation password matching check before enabling the "Register Token" button.
- **Usability Findings & Minor Flaws:**
  - *Observation:* If a user plugs in a USB while on the registration tab, they must click the "Refresh Drives" button to see the new drive letter.
  - *Recommendation for V1.1:* Connect native Windows `WM_DEVICECHANGE` directly to an auto-refresh trigger in `RegistrationView`.

### View 3: Authentication View (`app/authentication_view.py`)
- **Strengths:**
  - Clean, distraction-free authentication card.
  - Passphrase field automatically focuses upon opening the view.
  - Immediate memory clearing: `input_passphrase.clear()` is called both on success and failure to prevent text lingering in the widget buffer.
  - Clear, user-friendly error banners on failed challenge verification.

### View 4: Device Monitor View (`app/monitor_view.py`)
- **Strengths:**
  - Detailed physical hardware telemetry table (Drive Letter, Vendor, Product, Bus Interface, Serial Number, Partition Capacity, Free Space).
  - Prominent grace period countdown progress bar that animates smoothly during simulated disconnects.
  - Exclusion filter cleanly hides internal system disks (`C:\`, `D:\`).

### View 5: Security Logs View (`app/logs_view.py`)
- **Strengths:**
  - Real-time streaming table with timestamp, event type, status badge, and sanitized descriptions.
  - Live filter/search bar allows instant substring searching across descriptions, device UUIDs, and event types.
  - Single-click CSV export button for audit compliance.
- **Usability Findings & Minor Flaws:**
  - *Observation:* When many thousands of rows accumulate, full table reloading can take $>100$ ms.
  - *Recommendation for V1.1:* Implement virtualized QTableView with dynamic pagination (fetching 50 rows per batch).

### View 6: Settings View (`app/settings_view.py`)
- **Strengths:**
  - Clear sliders and spinboxes for Grace Period (1s to 60s).
  - Prominent warning box for **Simulation Mode**: *"When enabled, workstation lock is simulated safely without triggering Windows LockWorkStation."*
  - Instant persistence to SQLite database on value change.

### View 7: Recovery View (`app/recovery_view.py`)
- **Strengths:**
  - Empathetic, calming UX for emergency recovery situations.
  - Explains step-by-step how to log into Windows using native Windows PIN or password if the USB is lost.
  - Red-accented "Revoke Registered Device" button with a double-confirmation modal dialog to prevent accidental revocation.

---

## 3. Accessibility & High-DPI Compliance

- **High-DPI Scaling:** Tested at 100%, 125%, and 150% display scaling on Windows 11. Fonts and layout margins scale linearly without clipping.
- **Keyboard Navigation:** Tab order flows logically from top to bottom across form inputs and submit buttons.
- **Color Contrast:** Text contrast ratios exceed WCAG AA standards (white `#ffffff` on `#111726` slate background provides a contrast ratio of $14.2:1$).

