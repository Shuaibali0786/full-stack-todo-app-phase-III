@echo off
cls
echo ========================================
echo STARTING TASKFLOW AI FRONTEND
echo ========================================
echo.
echo Frontend will start on: http://localhost:3000
echo.
echo ========================================
echo.

echo [1/2] Checking Node.js...
node --version
echo.

echo [2/2] Starting Vite development server...
echo.
echo FRONTEND IS STARTING...
echo Press Ctrl+C to stop
echo.
echo ========================================
echo.

npm run dev
