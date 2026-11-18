## Build commands

Run these commands from the repository root on the target operating system.
Python and dependencies are included in the output; recipients do not need Python
or uv. Keep `launcher.py` as the PyInstaller entry point. Builds target the
architecture of the Python interpreter used to build them.

Both builds include the packaged default config. The macOS build also copies the
root `config.toml` beside its executable inside the app. Rebuilding replaces release files; save any
custom configuration and reports elsewhere first. These commands produce
unsigned releases and do not perform macOS notarization.

### Windows (PowerShell)

clean builds

```powershell
uv run --group dev pyinstaller --noconfirm --clean `
  --distpath dist/windows `
  --workpath build/windows `
  V11_Tools.spec

if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed" }
```

normal builds

```powershell
uv run --group dev pyinstaller --noconfirm `
  --distpath dist/windows `
  --workpath build/windows `
  V11_Tools.spec

if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed" }
```
