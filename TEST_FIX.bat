@echo off
echo ================================================
echo   TESTING IF BACKEND FIX IS WORKING
echo ================================================
echo.

echo Testing if backend returns 307 redirect (BAD) or 401 auth (GOOD)...
echo.

curl -X GET "http://localhost:8000/api/v1/tags/" -s -o nul -w "Status: %%{http_code}\n"

echo.
echo ================================================
echo RESULTS:
echo - If you see "Status: 401" = FIX IS WORKING! ✓
echo - If you see "Status: 307" = OLD CODE STILL RUNNING ✗
echo - If you see "Status: 000" = BACKEND NOT RUNNING ✗
echo ================================================
echo.

pause
