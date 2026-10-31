# Download the official Immich Compose file into the supplied NEW setup directory.
# This script does not overwrite files unless -Force is explicitly provided.
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$InstallDir,
    [switch]$Force
)
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
$composePath = Join-Path $InstallDir 'docker-compose.yml'
$envPath = Join-Path $InstallDir '.env'
if (((Test-Path $composePath -PathType Leaf) -or (Test-Path $envPath -PathType Leaf)) -and -not $Force) {
    throw 'Target already contains Immich configuration. Refusing to overwrite. Review files manually.'
}
Invoke-WebRequest -Uri 'https://github.com/immich-app/immich/releases/latest/download/docker-compose.yml' -OutFile $composePath
if (-not (Test-Path $envPath -PathType Leaf)) {
    Invoke-WebRequest -Uri 'https://github.com/immich-app/immich/releases/latest/download/example.env' -OutFile $envPath
}
Write-Host 'Downloaded upstream configuration. REVIEW and edit private .env, then configure pgdata: in Compose before starting.'
