@echo off
REM Setup: installs DrissionPage and checks for Chrome
echo 9Router Antigravity Bot - Setup
echo ================================
echo.

where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found. Install from python.org
    pause
    exit /b 1
)

echo Installing DrissionPage...
pip install DrissionPage

echo.
echo Setup complete.
echo.
echo   1. Create accounts.txt:  email^|password
echo   2. Run:  python bot.py
echo.
pause
