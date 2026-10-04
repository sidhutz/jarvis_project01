@echo off
setlocal
cd /d "%~dp0"

if exist "dist\Jarvis\Jarvis.exe" (
    start "" "dist\Jarvis\Jarvis.exe"
    exit /b 0
)

if exist "dist\run.exe" (
    echo Warning: launching the legacy build from dist\run.exe.
    echo Rebuild with build_app.bat after installing a working Python 3.11 runtime.
    start "" "dist\run.exe"
    exit /b 0
)

echo Jarvis app abhi build nahi hua.
echo Pehle build_app.bat double-click karein.
pause
