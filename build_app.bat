@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe -m PyInstaller run.spec --noconfirm
    goto :done
)

where pyinstaller >nul 2>nul
if %errorlevel%==0 (
    pyinstaller run.spec --noconfirm
    goto :done
)

where python >nul 2>nul
if %errorlevel%==0 (
    python -m PyInstaller run.spec --noconfirm
    goto :done
)

where py >nul 2>nul
if %errorlevel%==0 (
    py -m PyInstaller run.spec --noconfirm
    goto :done
)

echo Python/PyInstaller command nahi mila.
echo Pehle install karein:
echo   pip install pyinstaller
echo Phir is file ko dobara double-click karein.
pause
exit /b 1

:done
echo.
echo Build complete. App yahan milega:
echo   dist\Jarvis\Jarvis.exe
pause
