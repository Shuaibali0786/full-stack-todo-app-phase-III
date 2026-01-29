@echo off
REM ==============================================================================
REM TaskFlow AI - Backend Startup (SAFE MODE)
REM ==============================================================================
REM This script GUARANTEES the correct virtual environment is used
REM ==============================================================================

echo.
echo ========================================
echo   TaskFlow AI - Backend Startup (SAFE)
echo ========================================
echo.

cd /d "%~dp0"
echo [INFO] Working directory: %CD%
echo.

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found at: %CD%\venv
    echo [FIX] Please create venv first:
    echo        python -m venv venv
    echo        venv\Scripts\activate
    echo        pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo [1/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [2/5] Verifying Python location...
where python
echo.

REM Get Python path and check if it's from our venv
for /f "delims=" %%i in ('where python') do set PYTHON_PATH=%%i
echo Using Python: %PYTHON_PATH%

REM Check if Python is from the correct venv
echo %PYTHON_PATH% | find /i "%CD%\venv" >nul
if errorlevel 1 (
    echo.
    echo [ERROR] Wrong Python detected!
    echo Expected: %CD%\venv\Scripts\python.exe
    echo Actual:   %PYTHON_PATH%
    echo.
    echo [FIX] Please close ALL terminals and try again
    echo       Or manually run: venv\Scripts\activate
    echo.
    pause
    exit /b 1
)

echo [SUCCESS] Correct venv activated!
echo.

echo [3/5] Checking Python version...
python --version
echo.

echo [4/5] Verifying dependencies...
python -c "import fastapi; import sse_starlette; print('[OK] Core dependencies installed')"
if errorlevel 1 (
    echo.
    echo [ERROR] Dependencies missing!
    echo [FIX] Installing dependencies...
    pip install -r requirements.txt
    echo.
)

echo.
echo [5/5] Starting FastAPI server...
echo.
echo ========================================
echo   Server starting on http://0.0.0.0:8000
echo   Press Ctrl+C to stop
echo ========================================
echo.

python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

if errorlevel 1 (
    echo.
    echo [ERROR] Server failed to start!
    echo Check the error message above for details.
    echo.
    pause
)
