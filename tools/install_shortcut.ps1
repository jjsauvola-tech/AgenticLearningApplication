param(
    [string]$Executable = (Join-Path $PSScriptRoot 'ALA.exe'),
    [string]$DataDirectory = '',
    [string]$DesktopDirectory = [Environment]::GetFolderPath('DesktopDirectory')
)
$ErrorActionPreference = 'Stop'
$resolvedExecutable = (Resolve-Path -LiteralPath $Executable).Path
if ([IO.Path]::GetFileName($resolvedExecutable) -ne 'ALA.exe') { throw 'Expected ALA.exe' }
if (-not (Test-Path -LiteralPath $DesktopDirectory -PathType Container)) { throw 'Desktop folder not found' }
if ($DataDirectory.Contains('"')) { throw 'Invalid data directory' }
$shell = New-Object -ComObject WScript.Shell
$shortcutPath = Join-Path $DesktopDirectory 'ALA.lnk'
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $resolvedExecutable
$shortcut.WorkingDirectory = Split-Path -Parent $resolvedExecutable
$shortcut.IconLocation = "$resolvedExecutable,0"
$shortcut.Description = 'ALA - oma oppimistyotila / personal learning workspace'
if ($DataDirectory) { $shortcut.Arguments = '--data-dir "' + [IO.Path]::GetFullPath($DataDirectory) + '"' }
$shortcut.Save()
$verified = $shell.CreateShortcut($shortcutPath)
if ($verified.TargetPath -ne $resolvedExecutable) { throw 'Shortcut verification failed' }
Write-Output $shortcutPath
