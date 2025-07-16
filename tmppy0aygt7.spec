# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['/var/folders/vm/g6shz35s6sj32c9lshs3xr0c0000gn/T/tmppy0aygt7.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['pymediainfo'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='tmppy0aygt7',
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
