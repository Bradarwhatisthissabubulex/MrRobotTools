# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for MrRobotTools.
Build with: pyinstaller mrrobot.spec
"""

block_cipher = None

hidden_imports = [
    "core", "core.colors", "core.banner", "core.auth", "core.http",
    "modules",
    "modules.pentesting",
    "modules.pentesting.advanced_scanner",
    "modules.pentesting.vulnerability_scanner",
    "modules.pentesting.port_scanner",
    "modules.pentesting.url_crawler",
    "modules.pentesting.pinger",
    "modules.pentesting.host_discovery",
    "modules.osint",
    "modules.osint.dorking",
    "modules.osint.wallet_tracker",
    "modules.osint.username_tracker",
    "modules.osint.email_tracker",
    "modules.osint.email_lookup",
    "modules.osint.ip_lookup",
    "modules.osint.phone_lookup",
    "modules.osint.instagram_lookup",
    "modules.utils",
    "modules.utils.metadata_scanner",
    "modules.utils.metadata_deleter",
    "modules.utils.website_cloner",
    "whois", "bs4", "PIL", "exifread",
]

a = Analysis(
    ["mrrobot.py"],
    pathex=["."],
    binaries=[],
    datas=[],
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="MrRobotTools",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
