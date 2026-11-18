# -*- mode: python ; coding: utf-8 -*-

import glob
import importlib.util
import os

from PyInstaller.utils.hooks import collect_all


# Collect mssql-python dependencies
datas = [
    ('src/agent_state_mapper/default_config.toml', 'agent_state_mapper'),
    ('LICENSE', '.'),
]
binaries = []
hiddenimports = []

for package in ("mssql_python", "mssql_python_odbc", "mssql_py_core"):
    if importlib.util.find_spec(package) is not None:
        d, b, h = collect_all(package)
        datas.extend(d)
        binaries.extend(b)
        hiddenimports.extend(h)


# mssql-python dynamically loads its compiled DDBC bindings.
# Ensure the .pyd files exist in the expected package directory.
pkg_dir = os.path.dirname(
    importlib.util.find_spec("mssql_python").origin
)

pyd_files = glob.glob(
    os.path.join(pkg_dir, "ddbc_bindings.*.pyd")
)

if not pyd_files:
    raise RuntimeError("mssql-python DDBC bindings not found")

binaries.extend(
    (path, "mssql_python")
    for path in pyd_files
)


a = Analysis(
    ['launcher.py'],
    pathex=['src'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='V11_Tools',
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
    icon=['assets/app.ico'],
)
