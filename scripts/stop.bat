@echo off
setlocal

set SCRIPT_DIR=%~dp0
for %%I in ("%SCRIPT_DIR%..") do set ROOT_DIR=%%~fI

cd /d "%ROOT_DIR%"
docker compose down --remove-orphans
if errorlevel 1 (
  echo Failed to stop PM MVP app.
  exit /b 1
)

echo PM MVP app stopped.
