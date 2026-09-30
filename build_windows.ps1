param([string]$Python = 'python', [string]$Output = 'dist')
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
& $Python 'tools/generate_icon.py'
if ($LASTEXITCODE -ne 0) { throw 'ALA icon generation failed' }
& $Python -m PyInstaller --noconfirm --clean --onedir --windowed --name ALA --icon 'assets/ala.ico' --add-data 'web;web' --collect-all pypdfium2 --collect-all pypdfium2_raw --distpath $Output main.py
if ($LASTEXITCODE -ne 0) { throw 'ALA packaging failed' }
Copy-Item -LiteralPath 'README.md' -Destination (Join-Path $Output 'ALA\README.md')
Copy-Item -LiteralPath 'tools/install_shortcut.ps1' -Destination (Join-Path $Output 'ALA\install_shortcut.ps1')
& $Python 'tools/collect_notices.py' (Join-Path $Output 'ALA')
if ($LASTEXITCODE -ne 0) { throw 'Dependency notices could not be collected' }
