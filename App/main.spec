# main.spec
# -*- mode: python ; coding: utf-8 -*-

import subprocess

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['C:\\Users\\adham\\Documents\\GitHub\\Task-Management-App\\App'],
    binaries=[],
    datas=[
        ('Audio/*', 'Audio'),
        ('Icons/*', 'Icons'),
        ('Images/*', 'Images'),
        ('*.ui', '.'),
        ('*.qss', '.'),
        ('sort.png', '.')
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='tasky',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set console to False to remove the terminal window
    icon='appIcon.ico'
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main'
)

# Add the post-build script
post_build_script = 'rename_internal.py'
subprocess.run(['python', post_build_script])
