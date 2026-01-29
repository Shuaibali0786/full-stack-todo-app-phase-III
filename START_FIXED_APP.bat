@echo off
echo ========================================
echo TaskFlow AI - Fixed Chatbot Startup
echo ========================================
echo.

echo [1/4] Installing backend dependencies...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)
echo ✓ Backend dependencies installed
echo.

echo [2/4] Starting backend server...
start "Backend Server" cmd /k "cd /d %~dp0backend && uvicorn src.main:app --reload --port 8000"
echo ✓ Backend starting on http://localhost:8000
echo.

timeout /t 3 /nobreak >nul

echo [3/4] Installing frontend dependencies...
cd ..\frontend
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install frontend dependencies
    pause
    exit /b 1
)
echo ✓ Frontend dependencies installed
echo.

echo [4/4] Starting frontend server...
start "Frontend Server" cmd /k "cd /d %~dp0frontend && npm run dev"
echo ✓ Frontend starting on http://localhost:3000
echo.

echo ========================================
echo ✓ BOTH SERVERS STARTED SUCCESSFULLY
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo Dashboard: http://localhost:3000/dashboard
echo.
echo ========================================
echo TEST CHECKLIST:
echo ========================================
echo [ ] Can you see text as you type in chat input?
echo [ ] Does "hi" get a friendly response (not error)?
echo [ ] Does "add task buy milk tomorrow" create a task?
echo [ ] Does "show my tasks" list your tasks?
echo [ ] Are there NO MissingGreenlet errors in backend?
echo.
echo Press any key to exit this window (servers will keep running)
pause >nul
