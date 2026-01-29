@echo off
echo ========================================
echo   TaskFlow AI - Frontend Startup
echo ========================================
echo.

echo [1/2] Checking Node.js version...
node --version
npm --version
echo.

echo [2/2] Starting Next.js development server...
echo Frontend will be available at: http://localhost:3000
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

npm run dev

pause
