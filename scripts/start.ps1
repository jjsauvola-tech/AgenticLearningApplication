param([switch]$NoBrowser, [string]$DataDir)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
if (-not $DataDir) { $DataDir = Join-Path $env:LOCALAPPDATA 'ALA' }
$DataDir = [IO.Path]::GetFullPath($DataDir)
New-Item -ItemType Directory -Path $DataDir -Force | Out-Null

# Use the project environment first, then a Python already available on this PC.
$candidates = @(
    (Join-Path $projectRoot '.venv\Scripts\python.exe'),
    (Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe')
)
$installedPython = Get-Command python -ErrorAction SilentlyContinue
if ($installedPython) { $candidates += $installedPython.Source }
$pythonPath = $null
foreach ($candidate in $candidates) {
    if (Test-Path -LiteralPath $candidate) {
        & $candidate -c 'import docx, pptx, pypdf, pypdfium2, PIL' 2>$null
        if ($LASTEXITCODE -eq 0) { $pythonPath = $candidate; break }
    }
}
if (-not $pythonPath) {
    throw 'ALA needs its Python dependencies. Install requirements.txt in .venv, or use the packaged ALA.exe.'
}

$launchId = [guid]::NewGuid().ToString('N')
$runtimeFile = Join-Path $DataDir "launch-$launchId.json"
$errorLog = Join-Path $DataDir "launch-$launchId.log"
$arguments = @('"' + (Join-Path $projectRoot 'main.py') + '"',
    '--data-dir', '"' + $DataDir + '"', '--runtime-file', '"' + $runtimeFile + '"')
if ($NoBrowser) { $arguments += '--no-browser' }
$process = Start-Process -FilePath $pythonPath -ArgumentList $arguments -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardError $errorLog -PassThru
for ($attempt = 0; $attempt -lt 100; $attempt++) {
    if ($process.HasExited) {
        $details = Get-Content -LiteralPath $errorLog -Raw -ErrorAction SilentlyContinue
        throw "ALA could not start. $details"
    }
    if (Test-Path -LiteralPath $runtimeFile) {
        try {
            $runtime = Get-Content -LiteralPath $runtimeFile -Raw | ConvertFrom-Json
            $parts = $runtime.url -split '#', 2
            $state = Invoke-RestMethod -Uri ($parts[0] + 'api/state') -Headers @{'X-ALA-Token'=$parts[1]} -TimeoutSec 2
            Write-Output "ALA $($state.version) is running."
            Write-Output "Startup details: $runtimeFile"
            exit 0
        } catch { }
    }
    Start-Sleep -Milliseconds 150
}
throw "ALA startup timed out. Check $errorLog"
