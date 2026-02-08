@echo off
echo ============================================================
echo QUICK START - Full-Stack Todo App
echo ============================================================
echo.

echo [1/3] Verifying Backend Database Connection...
echo.
cd backend
python verify_neon_db.py
if errorlevel 1 (
    echo.
    echo ❌ Database verification failed!
    echo Please check your internet connection and Neon database URL.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo [2/3] Installing Backend Dependencies...
echo ============================================================
echo.
pip install -r requirements.txt

echo.
echo ============================================================
echo [3/3] Verifying Frontend Dependencies...
echo ============================================================
echo.
cd ..\frontend
if not exist "node_modules" (
    echo Installing npm packages...
    call npm install
) else (
    echo ✅ Frontend dependencies already installed
)

echo.
echo ============================================================
echo ✅ SETUP COMPLETE!
echo ============================================================
echo.
echo To start the application:
echo.
echo 1. Backend:  cd backend ^&^& uvicorn src.main:app --reload
echo 2. Frontend: cd frontend ^&^& npm run dev
echo.
echo Then open: http://localhost:3000
echo.
pause
