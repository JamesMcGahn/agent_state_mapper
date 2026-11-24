# -*- mode: python ; coding: utf-8 -*-

import glob
import importlib.util
import os
from pathlib import Path

from PyInstaller.utils.hooks import collect_all


# Resolve build inputs relative to this spec, including Git-ignored defaults.
project_root = Path(SPECPATH)
default_configs = project_root / 'src/agent_state_mapper/default_configs'
required_configs = (
    'app/default_config.toml',
    'states/common.toml',
    'states/avaya.toml',
)
missing_configs = [
    str(default_configs / name)
    for name in required_configs
    if not (default_configs / name).is_file()
]
if missing_configs:
    raise RuntimeError(
        'Required default configs are missing. These files are Git-ignored; '
        'provide them on the build machine before building:\n'
        + '\n'.join(missing_configs)
    )

# Collect mssql-python dependencies
datas = [
    (str(default_configs), 'agent_state_mapper/default_configs'),
    (str(project_root / 'LICENSE'), '.'),
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
    [str(project_root / 'launcher.py')],
    pathex=[str(project_root / 'src')],
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
    icon=[str(project_root / 'assets/app.ico')],
)
