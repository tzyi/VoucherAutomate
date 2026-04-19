# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['gui.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('settings.py', '.'),
        ('src/body.py', 'src'),
        ('src/head.py', 'src'),
        ('src/main.py', 'src'),
        ('src/read_excel.py', 'src'),
        ('src/toolbar_btn.py', 'src'),
    ],
    hiddenimports=[
        'pywinauto',
        'pywinauto.application',
        'pywinauto.keyboard',
        'pywinauto.timings',
        'openpyxl',
        'openpyxl.styles',
        'comtypes',
        'comtypes.client',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='VoucherAutomate',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='VoucherAutomate',
)
