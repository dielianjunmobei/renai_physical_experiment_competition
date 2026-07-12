$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Deploy = Join-Path $Root "deploy"

if (-not (Test-Path (Join-Path $Deploy "admin_api.py"))) {
    throw "Cannot find deploy\admin_api.py under: $Root"
}

Set-Location $Deploy

$AdminHost = if ($env:ADMIN_API_HOST) { $env:ADMIN_API_HOST } else { "127.0.0.1" }

uv run --python 3.13 --with-requirements requirements.txt `
    uvicorn admin_api:app `
    --host $AdminHost `
    --port 8601
