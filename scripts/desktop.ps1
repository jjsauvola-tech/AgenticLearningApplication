$ErrorActionPreference = 'Stop'
try {
    & (Join-Path $PSScriptRoot 'install-desktop.ps1') -Quiet
    & (Join-Path $PSScriptRoot 'start.ps1') -AgentUX -Latest
} catch {
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.MessageBox]::Show($_.Exception.Message, 'ALA startup', 'OK', 'Error') | Out-Null
    exit 1
}
