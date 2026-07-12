@echo off
setlocal

cd /d "%~dp0deploy"
if errorlevel 1 (
  echo Cannot enter deploy directory.
  pause
  exit /b 1
)

if not defined ADMIN_API_HOST set "ADMIN_API_HOST=127.0.0.1"
uv run --python 3.13 --with-requirements requirements.txt uvicorn admin_api:app --host %ADMIN_API_HOST% --port 8601

pause
