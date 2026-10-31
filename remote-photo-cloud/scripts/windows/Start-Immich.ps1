# Start an existing, locally configured Immich Docker Compose installation.
[CmdletBinding()]
param([string]$ImmichDir = 'C:\Immich')
$ErrorActionPreference = 'Stop'
$composePath = Join-Path $ImmichDir 'docker-compose.yml'
$envPath = Join-Path $ImmichDir '.env'
if (-not (Test-Path $composePath -PathType Leaf)) { throw 'Missing docker-compose.yml in the selected directory.' }
if (-not (Test-Path $envPath -PathType Leaf)) { throw 'Missing private .env; do not use the public example directly.' }
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { throw 'Docker CLI unavailable. Start Docker Desktop first.' }
Push-Location $ImmichDir
try {
    & docker compose config -q
    if ($LASTEXITCODE -ne 0) { throw 'Docker Compose config validation failed.' }
    & docker compose up -d
    if ($LASTEXITCODE -ne 0) { throw 'Docker Compose failed to start.' }
    & docker compose ps
    if ($LASTEXITCODE -ne 0) { throw 'Unable to list Immich services.' }
} finally {
    Pop-Location
}
