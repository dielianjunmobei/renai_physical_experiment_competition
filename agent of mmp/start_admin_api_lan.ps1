$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$AdminScript = Join-Path $Root "start_admin_api.ps1"

if (-not (Test-Path $AdminScript)) {
    throw "Cannot find start_admin_api.ps1 under: $Root"
}

$env:ADMIN_API_HOST = "0.0.0.0"
& $AdminScript
