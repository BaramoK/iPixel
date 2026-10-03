# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

# Chemin du projet
project_root = r"C:\Users\BaramoK\Documents\Git\iPixel"

# Collecte automatique des fichiers données de tkinterdnd2
tkdnd_datas = collect_data_files('tkinterdnd2')

block_cipher = None

a = Analysis(
    [os.path.join(project_root, 'app.py')],
    pathex=[project_root],
    binaries=[],
    datas=tkdnd_datas,
    hiddenimports=[
        'gui',
        'gui.main_window',
        'gui.image_tab',
        'gui.text_tab',
        'gui.history_tab',
        'gui.settings_tab',
        'tkinterdnd2',
        'pypixelcolor',
        'pypixelcolor.lib.font_config',
        'bleak',
        'bleak.backends',
        'bleak.backends.winrt',
        'bleak.backends.winrt.client',
        'bleak.backends.winrt.scanner',
    ],
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
    [],
    exclude_binaries=True,
    name='iPixel-UI-Manager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='iPixel-UI-Manager',
)