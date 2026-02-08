@echo off
echo ========================================
echo  Chatbot Production Fixes - Quick Start
echo ========================================
echo.

echo [1/3] Starting Backend Server...
start "FastAPI Backend" cmd /k "cd backend && python -m uvicorn src.main:app --reload"
timeout /t 5 /nobreak >nul

echo.
echo [2/3] Starting Frontend Server...
start "Next.js Frontend" cmd /k "cd frontend && npm run dev"
timeout /t 5 /nobreak >nul

echo.
echo [3/3] Opening Browser...
timeout /t 10 /nobreak >nul
start http://localhost:3000

echo.
echo ========================================
echo  Servers Started Successfully!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Test the chatbot with these commands:
echo  - "Hello" (warm greeting)
echo  - "add task I am going to Karachi" (instant task creation)
echo  - "show my tasks" (list tasks with emojis)
echo  - "complete task going to Karachi" (celebration!)
echo  - "thanks" (appreciation response)
echo.
echo See TEST_CHATBOT_FIXES.md for detailed testing guide
echo.
echo Press any key to exit (servers will keep running)...
pause >nul
