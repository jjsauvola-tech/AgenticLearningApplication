param([switch]$Quiet)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$versionText = Get-Content -LiteralPath (Join-Path $projectRoot 'ala\__init__.py') -Raw
$version = [regex]::Match($versionText, "__version__\s*=\s*'([^']+)'").Groups[1].Value
if (-not $version) { throw 'ALA version is missing.' }
$desktop = [Environment]::GetFolderPath('Desktop')
$shortcutPath = Join-Path $desktop "ALA $version.lnk"
$targetScript = Join-Path $PSScriptRoot 'desktop.ps1'
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
$shortcut.Arguments = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + $targetScript + '"'
$shortcut.WorkingDirectory = $projectRoot
$shortcut.Description = "ALA $version - latest local build, learning agents"
$shortcut.IconLocation = (Join-Path $env:SystemRoot 'System32\shell32.dll') + ',167'
$shortcut.WindowStyle = 7
$shortcut.Save()
# Only retire this project's own previous versioned shortcuts.
Get-ChildItem -LiteralPath $desktop -Filter 'ALA *.lnk' | ForEach-Object {
    if ($_.FullName -ne $shortcutPath) {
        $previous = $shell.CreateShortcut($_.FullName)
        if ($previous.Arguments -eq $shortcut.Arguments -and $previous.WorkingDirectory -eq $projectRoot) {
            Remove-Item -LiteralPath $_.FullName
        }
    }
}
if (-not $Quiet) { Write-Output $shortcutPath }
