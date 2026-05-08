@echo off
REM ============================================================
REM  CaiNiao Design - Vue3 Frontend Dev Server
REM  http://localhost:5173
REM ============================================================
set NODE_DIR=C:\Users\CNGG\.workbuddy\binaries\node\versions\22.12.0
set "PATH=%NODE_DIR%;%PATH%"
set NODE_OPTIONS=
cd /d D:\cainiao\vue3-app
echo.
echo ============================================================
echo   CaiNiao Design - Frontend Dev Server
echo   http://localhost:5173
echo ============================================================
echo.
call npm.cmd run dev
pause
