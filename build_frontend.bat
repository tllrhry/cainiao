@echo off
REM ============================================================
REM  CaiNiao Design - Build Frontend for Production
REM  Run this before starting Nginx for production preview
REM ============================================================

setlocal

set "FRONTEND_DIR=D:\cainiao\vue3-app"
set "NODE_DIR=C:\Users\CNGG\.workbuddy\binaries\node\versions\22.12.0"

title Cainiao Design - Build Production

echo.
echo ============================================================
echo   CaiNiao Design - Frontend Build
echo   Target: D:\cainiao\vue3-app\dist
echo ============================================================
echo.

echo [INFO] Clearing old dist folder...
if exist "%FRONTEND_DIR%\dist" (
    rmdir /s /q "%FRONTEND_DIR%\dist"
)
echo [OK] Old dist cleared.

echo.
echo [INFO] Building frontend...
set "PATH=%NODE_DIR%;%PATH%"
set "NODE_OPTIONS="
cd /d "%FRONTEND_DIR%"
call npm.cmd run build

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Build completed successfully!
echo ============================================================
echo.
echo   New files in: %FRONTEND_DIR%\dist
echo.
echo   Now start Nginx to preview production:
echo   - Run start_all.bat for all services
echo   - Or just: nginx.exe -p D:\cainiao\nginx-install\nginx-1.26.3 -s reload
echo.
pause
