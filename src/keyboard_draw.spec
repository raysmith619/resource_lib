# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['cli.py'],
             pathex=['../../resource_lib/src', 'C:\\Users\\raysm\\workspace\\python\\keyboard_draw_prj\\src'],
             binaries=[],
             datas=[('keyboard_draw_hello.txt', '.'), ('hello_family.txt', '.'), ('../../resource_lib/images', './images')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='keyboard_draw',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='keyboard_draw')
