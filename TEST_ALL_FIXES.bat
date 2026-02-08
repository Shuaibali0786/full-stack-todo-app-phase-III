@echo off
echo ========================================
echo TESTING ALL FIXES
echo ========================================
echo.

echo [1/5] Testing Backend Health...
curl -s http://localhost:8000/health
echo.
echo.

echo [2/5] Testing Auth Endpoint (POST /api/v1/login)...
echo Expected: 401 for invalid credentials
curl -s -X POST http://localhost:8000/api/v1/login -H "Content-Type: application/json" -d "{\"email\":\"test@example.com\",\"password\":\"wrongpass\"}"
echo.
echo.

echo [3/5] Testing Priorities Endpoint WITHOUT Auth (should fail with 401)...
echo Expected: 401 Unauthorized
curl -s http://localhost:8000/api/v1/priorities/
echo.
echo.

echo [4/5] Testing Tags Endpoint WITHOUT Auth (should fail with 401)...
echo Expected: 401 Unauthorized
curl -s http://localhost:8000/api/v1/tags/
echo.
echo.

echo [5/5] Testing Tasks Endpoint WITHOUT Auth (should fail with 401)...
echo Expected: 401 Unauthorized
curl -s "http://localhost:8000/api/v1/tasks/?sort=created_at&order=desc&limit=25&offset=0"
echo.
echo.

echo ========================================
echo TEST COMPLETE
echo ========================================
echo.
echo Next Steps:
echo 1. If backend is not running, start it: cd backend ^&^& uvicorn src.main:app --reload
echo 2. Start frontend: npm run dev
echo 3. Test login flow in browser
echo 4. Verify no console errors on dashboard
echo.
pause
