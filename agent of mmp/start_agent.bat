@echo off
setlocal

cd /d "%~dp0deploy"
if errorlevel 1 (
  echo Cannot enter deploy directory.
  pause
  exit /b 1
)

set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
set STREAMLIT_SERVER_HEADLESS=true

uv run --python 3.13 --with-requirements requirements.txt streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true --browser.gatherUsageStats false

pause
