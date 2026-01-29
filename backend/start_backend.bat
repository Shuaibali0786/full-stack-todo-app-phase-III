@echo off
echo ========================================
echo   TaskFlow AI - Backend Startup
echo ========================================
echo.

echo [1/3] Activating virtual environment...
call venv\Scripts\activate

echo.
echo [2/3] Checking Python and dependencies...
python --version
echo.

echo [3/3] Starting FastAPI server...
echo Backend will be available at: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

pause
