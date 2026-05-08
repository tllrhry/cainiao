@echo off
REM ============================================================
REM  CaiNiao Design - Stop All Services
REM  Stops: Frontend -> Backend -> Nginx -> MySQL Container
REM ============================================================

set "NGINX_EXE=D:\cainiao\nginx-install\nginx-1.26.3\nginx.exe"
set "MYSQL_CONTAINER=mysql-portal"

title Cainiao Design - Stop Services

echo.
echo ============================================================
echo   CaiNiao Design - Stop All Services
echo ============================================================
echo.

REM ============================================================
REM Step 1: Stop Frontend (Node/Vite)
REM ============================================================
echo [1/4] Stopping Frontend...
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq node.exe" /fo list 2^>nul ^| find "PID:"') do (
    taskkill /PID %%a /F >nul 2>&1
)
echo [OK] Frontend stopped.

REM ============================================================
REM Step 2: Stop Backend (Python/Uvicorn)
REM ============================================================
echo.
echo [2/4] Stopping Backend...
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /fo list 2^>nul ^| find "PID:"') do (
    taskkill /PID %%a /F >nul 2>&1
)
echo [OK] Backend stopped.

REM ============================================================
REM Step 3: Stop Nginx
REM ============================================================
echo.
echo [3/4] Stopping Nginx...
if exist "%NGINX_EXE%" (
    "%NGINX_EXE%" -p "%NGINX_DIR%" -s stop 2>nul
)
REM Also kill any remaining nginx processes
taskkill /IM nginx.exe /F >nul 2>&1
echo [OK] Nginx stopped.

REM ============================================================
REM Step 4: Stop MySQL Container (optional - comment out to keep DB running)
REM ============================================================
echo.
echo [4/4] Stopping MySQL container...
echo [INFO] Skipping MySQL stop - container will keep running for persistence.
echo [INFO] To stop MySQL, run: podman stop %MYSQL_CONTAINER%
REM Uncomment the following line to stop MySQL:
REM podman stop %MYSQL_CONTAINER% >nul 2>&1

REM ============================================================
REM Summary
REM ============================================================
echo.
echo ============================================================
echo   Services stopped (except MySQL).
echo ============================================================
echo.
pause
