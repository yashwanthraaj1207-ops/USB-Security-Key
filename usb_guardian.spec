# -*- mode: python ; coding: utf-8 -*-
"""
USB Guardian - PyInstaller Specification File
Reproducible standalone Windows x64 packaging definition for Release Candidate 1 (RC1).
"""

import sys
import os
from pathlib import Path

block_cipher = None

project_root = os.path.abspath(SPECPATH)

datas = [
    (os.path.join(project_root, 'assets'), 'assets'),
    (os.path.join(project_root, 'config'), 'config'),
]

hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'cryptography',
    'cryptography.hazmat.primitives.asymmetric.ed25519',
    'cryptography.hazmat.primitives.ciphers.aead',
    'cryptography.hazmat.primitives.kdf.argon2',
    'cryptography.hazmat.primitives.kdf.pbkdf2',
    'cryptography.hazmat.primitives.hashes',
    'psutil',
    'sqlite3',
    'ctypes',
    'ctypes.wintypes',
    'uuid',
    'json',
    'hashlib',
    'hmac',
    'win32crypt',
    'winreg',
    'core.passkey_store',
]

excludes = [
    'pytest',
    'unittest',
    'scipy',
    'numpy',
    'matplotlib',
    'pandas',
    'tkinter',
    'torch',
    'transformers',
    'cv2',
    'PIL.TkImagePlugin',
]

a = Analysis(
    ['main.py'],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='USB Guardian',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # Windowed GUI application
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_root, 'assets', 'icons', 'app_icon.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='USB Guardian',
)

