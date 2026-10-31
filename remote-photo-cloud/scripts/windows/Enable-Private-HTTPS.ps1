# Share a local Immich service privately inside Tailscale with HTTPS.
# Do NOT use tailscale funnel: that would expose the service publicly.
[CmdletBinding()]
param([int]$ImmichPort = 2283)
$ErrorActionPreference = 'Stop'
if ($ImmichPort -lt 1 -or $ImmichPort -gt 65535) { throw 'Invalid TCP port.' }
if (-not (Get-Command tailscale -ErrorAction SilentlyContinue)) { throw 'Tailscale CLI is missing.' }
& tailscale serve --bg $ImmichPort
if ($LASTEXITCODE -ne 0) { throw 'Tailscale Serve setup failed.' }
Write-Host 'Tailscale Serve configured. The URL below belongs only in private local settings:'
& tailscale serve status
