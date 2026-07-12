$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Deploy = Join-Path $Root "deploy"

if (-not (Test-Path (Join-Path $Deploy "app.py"))) {
    throw "Cannot find deploy\app.py under: $Root"
}

Set-Location $Deploy

$env:STREAMLIT_BROWSER_GATHER_USAGE_STATS = "false"
$env:STREAMLIT_SERVER_HEADLESS = "true"

uv run --python 3.13 --with-requirements requirements.txt `
    streamlit run app.py `
    --server.port 8501 `
    --server.address 0.0.0.0 `
    --server.headless true `
    --browser.gatherUsageStats false
