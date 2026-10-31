# Check local Immich, Docker, and Tailscale Serve without printing secrets.
[CmdletBinding()]
param([string]$ImmichDir = 'C:\Immich')
$ErrorActionPreference = 'Stop'
if (-not (Test-Path (Join-Path $ImmichDir 'docker-compose.yml') -PathType Leaf)) {
    throw 'Immich Compose file not found in the selected directory.'
}
Push-Location $ImmichDir
try {
    & docker compose ps
    if ($LASTEXITCODE -ne 0) { throw 'Docker Compose could not list services.' }
} finally { Pop-Location }

$port = Test-NetConnection -ComputerName 'localhost' -Port 2283 -InformationLevel Quiet -WarningAction SilentlyContinue
if ($port) { Write-Host 'OK: local Immich port is reachable.' }
else { Write-Warning 'Immich local port is not reachable.' }
if (Get-Command tailscale -ErrorAction SilentlyContinue) {
    # This can display your private tailnet hostname in YOUR terminal; do not publish logs.
    & tailscale serve status
} else {
    Write-Warning 'Tailscale CLI not found.'
}
