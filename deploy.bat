@echo off
REM Full-Stack Todo App - Deployment Helper Script
echo ============================================
echo Full-Stack Todo App - Deployment Helper
echo ============================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed or not in PATH
    echo Please install Git from: https://git-scm.com/
    pause
    exit /b 1
)

REM Check current git status
echo [1/6] Checking Git status...
git status
echo.

REM Ask user to commit changes
echo [2/6] Ready to commit changes?
set /p COMMIT_MSG="Enter commit message (or 'skip' to skip): "

if /i not "%COMMIT_MSG%"=="skip" (
    echo Committing changes...
    git add .
    git commit -m "%COMMIT_MSG%"

    echo.
    echo Push to GitHub?
    set /p PUSH_CONFIRM="Push to GitHub? (y/n): "
    if /i "%PUSH_CONFIRM%"=="y" (
        git push origin master
        echo Changes pushed to GitHub!
    )
)

echo.
echo [3/6] Backend Deployment Status
echo ================================
echo Your backend should be deployed to HuggingFace Spaces
echo URL: https://shuaibali-todo-backend.hf.space
echo.
echo Testing backend health...
curl -s https://shuaibali-todo-backend.hf.space/health
echo.
echo.

echo [4/6] Frontend Build Test
echo =========================
echo Testing frontend build locally...
cd frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
)

echo.
echo Building frontend...
call npm run build

if errorlevel 1 (
    echo.
    echo ERROR: Frontend build failed!
    echo Please fix the errors above before deploying to Vercel.
    cd ..
    pause
    exit /b 1
)

echo.
echo SUCCESS: Frontend builds successfully!
cd ..

echo.
echo [5/6] Deployment Instructions
echo ==============================
echo.
echo BACKEND (HuggingFace):
echo 1. Go to: https://huggingface.co/spaces
echo 2. Find your space: shuaibali-todo-backend
echo 3. Update environment variables with new DATABASE_URL
echo 4. Click "Factory reboot"
echo.
echo FRONTEND (Vercel):
echo.
echo Option A - Vercel Dashboard (Recommended):
echo 1. Go to: https://vercel.com/new
echo 2. Import from GitHub: full-stack-todo-app-phase-III
echo 3. Set Root Directory to: frontend
echo 4. Add environment variable:
echo    NEXT_PUBLIC_API_URL = https://shuaibali-todo-backend.hf.space
echo 5. Click Deploy!
echo.
echo Option B - Vercel CLI:
echo 1. Install: npm install -g vercel
echo 2. Run: cd frontend
echo 3. Run: vercel login
echo 4. Run: vercel --prod
echo 5. Add env: vercel env add NEXT_PUBLIC_API_URL production
echo 6. Redeploy: vercel --prod
echo.

echo [6/6] Post-Deployment Checklist
echo ================================
echo After deploying, test these:
echo [ ] Frontend loads at your Vercel URL
echo [ ] Can register new account
echo [ ] Can login
echo [ ] Dashboard shows tasks
echo [ ] Can create/edit/delete tasks
echo [ ] No CORS errors in console
echo [ ] No 422/405 errors
echo [ ] AI chat works
echo.

echo ============================================
echo Deployment preparation complete!
echo Read VERCEL_DEPLOYMENT_GUIDE.md for detailed instructions
echo ============================================
pause
