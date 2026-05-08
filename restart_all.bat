@echo off
REM ============================================================
REM  CaiNiao Design - Restart All Services
REM  Stops and starts all services in sequence
REM ============================================================

echo.
echo ============================================================
echo   CaiNiao Design - Restarting Services
echo ============================================================
echo.

REM Stop all services
call stop_all.bat >nul 2>&1

echo.
echo Waiting 3 seconds before restart...
timeout /t 3 /nobreak >nul

REM Start all services
call start_all.bat

pause
