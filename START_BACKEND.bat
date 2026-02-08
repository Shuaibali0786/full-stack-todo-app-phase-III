@echo off
cls
echo ========================================
echo STARTING TASKFLOW AI BACKEND SERVER
echo ========================================
echo.
echo Backend will start on: http://localhost:8000
echo API docs will be at: http://localhost:8000/docs
echo.
echo ========================================
echo.

cd backend
echo [1/3] Checking Python environment...
python --version
echo.

echo [2/3] Verifying dependencies...
python -m pip show uvicorn > nul 2>&1
if errorlevel 1 (
    echo ERROR: uvicorn not installed!
    echo Run: pip install -r requirements.txt
    pause
    exit /b 1
)
echo Dependencies OK
echo.

echo [3/3] Starting server with uvicorn...
echo.
echo BACKEND IS STARTING...
echo Press Ctrl+C to stop
echo.
echo ========================================
echo.

python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
