@echo off
echo ================================================
echo   FORCE RESTARTING BACKEND WITH NEW CODE
echo ================================================
echo.

echo [1/4] Killing old backend processes...
taskkill /F /IM python.exe /FI "MEMUSAGE gt 50000" 2>nul
if %errorlevel% equ 0 (
    echo      Old backend killed successfully!
) else (
    echo      No old backend found (that's OK)
)

echo.
echo [2/4] Waiting 3 seconds for cleanup...
timeout /t 3 /nobreak >nul

echo.
echo [3/4] Starting backend with NEW code...
cd /d D:\phase-III\full-stack-todo-app-phase-III\backend

echo.
echo [4/4] Backend starting - DO NOT CLOSE THIS WINDOW!
echo ================================================
echo.
echo When you see "Application startup complete":
echo 1. Go to browser
echo 2. Press Ctrl+Shift+R to refresh dashboard
echo 3. Check if 422 errors are gone
echo.
echo ================================================
echo.

python -m uvicorn src.main:app --reload --log-level info

pause
