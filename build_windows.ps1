param([string]$Python = 'python', [string]$Output = 'dist')
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
& $Python -m PyInstaller --noconfirm --clean --onedir --windowed --name ALA --add-data 'web;web' --collect-all pypdfium2 --collect-all pypdfium2_raw --distpath $Output main.py
if ($LASTEXITCODE -ne 0) { throw 'ALA packaging failed' }
Copy-Item -LiteralPath 'README.md' -Destination (Join-Path $Output 'ALA\README.md')
& $Python 'tools/collect_notices.py' (Join-Path $Output 'ALA')
if ($LASTEXITCODE -ne 0) { throw 'Dependency notices could not be collected' }
