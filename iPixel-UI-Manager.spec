# -*- mode: python ; coding: utf-8 -*-

import sys
import os
import importlib.util
from PyInstaller.utils.hooks import collect_data_files

# Chemin du projet (dossier contenant ce fichier .spec)
project_root = os.path.abspath(SPECPATH)

# Collecte automatique des fichiers données
tkdnd_datas = collect_data_files('tkinterdnd2')

# ============================================================
# Collecte complète des données de pypixelcolor
# ============================================================
# collect_data_files détecte automatiquement les fichiers non-Python
# dans le package (polices .otf, fichiers de licence, etc.)
pypixel_datas = collect_data_files('pypixelcolor')

# Sécurité : on résout explicitement le chemin du package
# (sur l'environnement de build, pas en mode frozen)
pypixel_spec = importlib.util.find_spec('pypixelcolor')
if pypixel_spec and pypixel_spec.origin:
    pypixel_pkg = os.path.dirname(pypixel_spec.origin)

    # Le dossier 'fonts/' (contient unifont.otf)
    fonts_dir = os.path.join(pypixel_pkg, 'fonts')
    if os.path.isdir(fonts_dir):
        # On ajoute chaque fichier individuellement pour éviter
        # les doublons si collect_data_files l'a déjà traité
        for entry in os.listdir(fonts_dir):
            src = os.path.join(fonts_dir, entry)
            dst = os.path.join('pypixelcolor', 'fonts', entry)
            if (src, os.path.dirname(dst)) not in pypixel_datas:
                pypixel_datas.append((src, os.path.dirname(dst)))

# ============================================================
# Fichiers de données statiques du projet
# ============================================================
project_datas = [
    (os.path.join(project_root, 'config.json'), '.'),
    (os.path.join(project_root, 'history.json'), '.'),
]

# Le dossier gui/ : on inclut tous les fichiers .py individuellement
# pour qu'ils soient copiés même s'ils sont dans les hiddenimports
gui_dir = os.path.join(project_root, 'gui')
if os.path.isdir(gui_dir):
    for entry in os.listdir(gui_dir):
        if entry.endswith('.py'):
            src = os.path.join(gui_dir, entry)
            pypixel_datas.append((src, 'gui'))

all_datas = tkdnd_datas + pypixel_datas + project_datas

block_cipher = None

a = Analysis(
    [os.path.join(project_root, 'app.py')],
    pathex=[project_root],
    binaries=[],
    datas=all_datas,
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
        'pypixelcolor.commands.send_text',
        'pypixelcolor.commands.send_text.font_utils',
        'pypixelcolor.commands.send_text.image_processing',
        'pypixelcolor.commands.send_text.encoding',
        'pypixelcolor.commands.send_text.color_utils',
        'pypixelcolor.lib.emoji_manager',
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