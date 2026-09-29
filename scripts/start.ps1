param([switch]$NoBrowser, [string]$DataDir, [switch]$AgentUX, [switch]$Latest)
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

if ($Latest) {
    Push-Location $projectRoot
    try { $desiredBuild = & $pythonPath -c 'from ala.build import build_id; print(build_id())' }
    finally { Pop-Location }
    if ($LASTEXITCODE -ne 0) { throw 'Could not identify the current ALA build.' }
    $instancePath = Join-Path $DataDir 'instance.json'
    if (Test-Path -LiteralPath $instancePath) {
        $running = Get-Content -LiteralPath $instancePath -Raw | ConvertFrom-Json
        if ($running.build -ne $desiredBuild) {
            $runningParts = $running.url -split '#', 2
            $alive = $false
            try {
                $null = Invoke-RestMethod -Uri ($runningParts[0] + 'api/ping') -Headers @{'X-ALA-Token'=$runningParts[1]} -TimeoutSec 2
                $alive = $true
            } catch { }
            if ($alive) {
                $null = Invoke-RestMethod -Method Post -Uri ($runningParts[0] + 'api/shutdown') -Headers @{'X-ALA-Token'=$runningParts[1]} -Body '{}' -ContentType 'application/json' -TimeoutSec 5
                $oldProcess = Get-Process -Id $running.pid -ErrorAction SilentlyContinue
                if ($oldProcess -and -not $oldProcess.WaitForExit(30000)) {
                    throw 'ALA is finishing an operation. Wait a moment and open the shortcut again. No process was forced to stop.'
                }
            }
        }
    }
}

$launchId = [guid]::NewGuid().ToString('N')
$runtimeFile = Join-Path $DataDir "launch-$launchId.json"
$errorLog = Join-Path $DataDir "launch-$launchId.log"
$arguments = @('"' + (Join-Path $projectRoot 'main.py') + '"',
    '--data-dir', '"' + $DataDir + '"', '--runtime-file', '"' + $runtimeFile + '"')
$arguments += '--no-browser'
$process = Start-Process -FilePath $pythonPath -ArgumentList $arguments -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardError $errorLog -PassThru
for ($attempt = 0; $attempt -lt 100; $attempt++) {
    if (Test-Path -LiteralPath $runtimeFile) {
        try {
            $runtime = Get-Content -LiteralPath $runtimeFile -Raw | ConvertFrom-Json
            $parts = $runtime.url -split '#', 2
            $state = Invoke-RestMethod -Uri ($parts[0] + 'api/state') -Headers @{'X-ALA-Token'=$parts[1]} -TimeoutSec 2
            if ($Latest -and $runtime.build -ne $desiredBuild) { throw 'An older ALA process is still running.' }
            if (-not $NoBrowser) {
                $openUrl = $runtime.url
                if ($AgentUX) { $openUrl = $parts[0] + '?ux=agents#' + $parts[1] }
                Push-Location $projectRoot
                try { & $pythonPath -c 'import sys; from main import launch_browser; launch_browser(sys.argv[1])' $openUrl }
                finally { Pop-Location }
                if ($LASTEXITCODE -ne 0) { throw 'Could not open the ALA browser.' }
            }
            Write-Output "ALA $($state.version) is running."
            Write-Output "Startup details: $runtimeFile"
            exit 0
        } catch { }
    }
    if ($process.HasExited) {
        $details = Get-Content -LiteralPath $errorLog -Raw -ErrorAction SilentlyContinue
        throw "ALA could not start. $details"
    }
    Start-Sleep -Milliseconds 150
}
throw "ALA startup timed out. Check $errorLog"
