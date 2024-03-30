import sys
import os


from kivy_deps import sdl2, glew
from kivymd import hooks_path as kivymd_hooks_path

path = os.path.abspath("D:/projects/ReportGen/kivyApp")
path_data = os.path.abspath("D:/projects/ReportGen/kivyApp/resources")

a = Analysis(
    ["reportGen.py"],
    pathex=[path],
    binaries=[],
    datas=[(path_data, "resources")],
    hiddenimports=['pkg_resources.py2_warn'],
    hookspath=[kivymd_hooks_path,
    "D:/projects/ReportGen/kivyApp"],
    runtime_hooks=[],
    excludes=["*.exe"],  # Exclude executable files
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
    icon="D:/projects/ReportGen/kivyApp/resources/GIT logo.ico",
    debug=False,
    strip=False,
    upx=True,
    name="reportGen",
    console=False,
)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
               strip=False,
               upx=True,
               name='dist/resources')