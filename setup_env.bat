@echo off
setlocal enabledelayedexpansion

echo ============================================
echo   Cainiao Design - Setup
echo ============================================
echo.

set PYTHON=C:\Users\CNGG\.workbuddy\binaries\python\versions\3.13.12\python.exe
set VENV=C:\Users\CNGG\.workbuddy\binaries\python\envs\cainiao
set PIP=%VENV%\Scripts\pip.exe
set PY=%VENV%\Scripts\python.exe

cd /d D:\cainiao\backend

:: Step 1: Create venv
echo [1/3] Creating Python virtual environment...
if not exist "%VENV%\Scripts\python.exe" (
    "%PYTHON%" -m venv "%VENV%"
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo   Done.
) else (
    echo   Already exists, skipping.
)

:: Step 2: Install dependencies
echo.
echo [2/3] Installing Python packages...
"%PIP%" install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if %ERRORLEVEL% neq 0 (
    echo ERROR: Package install failed. Check network or pip config.
    pause
    exit /b 1
)
echo   Done.

:: Step 3: Create database tables + seed admin
echo.
echo [3/3] Creating database tables + seeding data...
echo   Make sure MySQL is running on localhost:3306
"%PY%" setup_db.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Database setup failed.
    echo   - Is MySQL running? Check: docker ps / podman ps
    echo   - Did you create the database? mysql -u root -p"Cainiao@123" -e "CREATE DATABASE IF NOT EXISTS cainiao_design"
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Setup Complete!
echo.
echo   Start backend: start_backend.bat
echo   Start frontend: cd vue3-app ^&^& npm run dev
echo ============================================
echo.
pause
