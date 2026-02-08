@echo off
cls
echo ========================================
echo RESTARTING BACKEND WITH FIX APPLIED
echo ========================================
echo.
echo CRITICAL FIX: Import error in deps.py has been fixed
echo The 'select' import was at the bottom of the file
echo causing 422 errors instead of proper auth errors.
echo.
echo ========================================
echo.
echo ACTION: Please STOP the current backend (Ctrl+C) if running
echo Then run this command:
echo.
echo   cd backend
echo   uvicorn src.main:app --reload
echo.
echo ========================================
echo.
echo After backend restarts, refresh your browser and test:
echo 1. Login to dashboard
echo 2. Check console - NO MORE 422 errors!
echo 3. Tasks should load successfully
echo.
pause
