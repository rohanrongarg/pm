@echo off
setlocal

set SCRIPT_DIR=%~dp0
for %%I in ("%SCRIPT_DIR%..") do set ROOT_DIR=%%~fI

cd /d "%ROOT_DIR%"
docker compose up --build -d
if errorlevel 1 (
  echo Failed to start PM MVP app.
  exit /b 1
)

echo PM MVP app is running at http://localhost:8000
