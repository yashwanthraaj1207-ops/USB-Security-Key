"""
USB Guardian - Application Entry Point
Starts the PySide6 Graphical User Interface or background access watchdog daemon.
"""

import sys
import argparse
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from core.resource_path import get_resource_path
from database.db_manager import DatabaseManager
from core.security_logger import SecurityLogger
from core.key_manager import KeyManager
from core.challenge_manager import ChallengeManager
from core.authenticator import Authenticator
from core.usb_detector import USBDetector
from core.session_manager import SessionManager
from core.usb_monitor import USBMonitor
from windows.session_lock import WindowsSessionLocker
from app.main_window import MainWindow


def main():
    parser = argparse.ArgumentParser(description="USB Guardian - Windows 11 Physical Authentication & Access Control")
    parser.add_argument(
        "--simulate-lock",
        action="store_true",
        help="Run in lock simulation mode (safe demonstration without locking real Windows desktop).",
    )
    parser.add_argument(
        "--service",
        action="store_true",
        help="Run as a headless background monitoring service without graphical interface.",
    )
    parser.add_argument(
        "--tray",
        action="store_true",
        help="Launch minimized directly to the system tray (for Windows boot startup persistence).",
    )
    args = parser.parse_args()

    # Headless background service mode
    if args.service:
        from windows.service.background_service import BackgroundService
        print("[*] Starting USB Guardian Background Service daemon...")
        service = BackgroundService(simulate_lock=args.simulate_lock)
        service.run()
        return

    # Graphical Desktop Mode
    app = QApplication(sys.argv)
    app.setApplicationName("USB Guardian")
    app.setOrganizationName("CyberSecurity")

    icon_path = get_resource_path("assets/icons/app_icon.ico")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Initialize subsystems
    db_manager = DatabaseManager()
    security_logger = SecurityLogger(db_manager)
    key_manager = KeyManager(db_manager, security_logger)
    challenge_manager = ChallengeManager()
    authenticator = Authenticator(key_manager, challenge_manager, security_logger)
    usb_detector = USBDetector()

    # Load persistent settings
    grace_period = int(db_manager.get_setting("grace_period_seconds", "5"))
    master_prot = db_manager.get_setting("master_protection_enabled", "true").lower() == "true"
    auto_lock_setting = db_manager.get_setting("auto_lock_enabled", "true").lower() == "true"
    effective_autolock = master_prot and auto_lock_setting
    stored_simulate = db_manager.get_setting("simulation_mode", "true").lower() == "true"
    effective_simulate = args.simulate_lock or stored_simulate
    lock_mode = db_manager.get_setting("lock_screen_mode", "guardian_overlay")

    # Synchronize Windows boot startup persistence if master protection is armed
    from windows.startup import is_startup_enabled, set_startup_enabled
    if master_prot and not is_startup_enabled():
        set_startup_enabled(True)

    session_manager = SessionManager(
        grace_period_seconds=grace_period,
        auto_lock_enabled=effective_autolock,
    )

    session_locker = WindowsSessionLocker(simulate=effective_simulate, mode=lock_mode)

    usb_monitor = USBMonitor(
        usb_detector=usb_detector,
        session_manager=session_manager,
        key_manager=key_manager,
        security_logger=security_logger,
        session_locker=session_locker,
        poll_interval=1.0,
        authenticator=authenticator,
    )

    # Start background monitor thread
    usb_monitor.start()
    security_logger.log("APP_STARTED", "INFO", "USB Guardian desktop application started.")

    # Create and display GUI
    window = MainWindow(
        db_manager=db_manager,
        security_logger=security_logger,
        key_manager=key_manager,
        session_manager=session_manager,
        authenticator=authenticator,
        usb_detector=usb_detector,
        usb_monitor=usb_monitor,
        session_locker=session_locker,
    )
    if args.tray:
        window.hide()
    else:
        window.show()

    # Clean exit handling
    exit_code = app.exec()
    usb_monitor.stop()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

