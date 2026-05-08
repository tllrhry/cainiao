@echo off
REM ============================================================
REM  CaiNiao Design - All-in-One Startup Script
REM  Starts: Podman Machine -> MySQL -> Nginx -> Backend -> Frontend
REM  Access: http://localhost (via Nginx port 80)
REM ============================================================

setlocal EnableDelayedExpansion

set "NGINX_DIR=D:\cainiao\nginx-install\nginx-1.26.3"
set "NGINX_EXE=%NGINX_DIR%\nginx.exe"
set "BACKEND_DIR=D:\cainiao\backend"
set "PYTHON_EXE=C:\Users\CNGG\.workbuddy\binaries\python\envs\cainiao\Scripts\python.exe"
set "FRONTEND_DIR=D:\cainiao\vue3-app"
set "NODE_DIR=C:\Users\CNGG\.workbuddy\binaries\node\versions\22.12.0"
set "MYSQL_CONTAINER=mysql-portal"
set "PODMAN_MACHINE=podman-machine-default"

title Cainiao Design - Startup

echo.
echo ============================================================
echo   CaiNiao Design - All-in-One Startup
echo   Access: http://localhost
echo ============================================================
echo.

REM ============================================================
REM Step 1: Start Podman Machine
REM ============================================================
echo [1/5] Checking Podman Machine...

podman machine inspect %PODMAN_MACHINE% >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Podman machine "%PODMAN_MACHINE%" not found.
    echo [INFO] Please run: podman machine init
    pause
    exit /b 1
)

REM Check if already running
podman machine inspect %PODMAN_MACHINE% 2>nul | findstr /C:"\"State\": \"running\"" >nul 2>&1
if not errorlevel 1 (
    echo [OK] Podman machine is already running.
) else (
    echo [INFO] Starting Podman machine "%PODMAN_MACHINE%"...
    podman machine start %PODMAN_MACHINE%
    if errorlevel 1 (
        echo [ERROR] Failed to start Podman machine.
        pause
        exit /b 1
    )
    echo [OK] Podman machine started.
)

REM Wait for Podman socket to be ready
echo [INFO] Waiting for Podman to initialize...
timeout /t 5 /nobreak >nul

REM ============================================================
REM Step 2: Start MySQL Container
REM ============================================================
echo.
echo [2/5] Checking MySQL container "%MYSQL_CONTAINER%"...

podman ps -a --format "{{.Names}}" 2>nul | findstr /C:"%MYSQL_CONTAINER%" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] MySQL container "%MYSQL_CONTAINER%" not found.
    echo [INFO] Please create it manually or check container name.
    pause
    exit /b 1
)

REM Check if already running
podman ps --format "{{.Names}}" 2>nul | findstr /C:"%MYSQL_CONTAINER%" >nul 2>&1
if not errorlevel 1 (
    echo [OK] MySQL container is already running.
) else (
    echo [INFO] Starting MySQL container...
    podman start %MYSQL_CONTAINER%
    if errorlevel 1 (
        echo [ERROR] Failed to start MySQL container.
        pause
        exit /b 1
    )
    echo [OK] MySQL container started.
    echo [INFO] Waiting for MySQL to be ready...
    timeout /t 8 /nobreak >nul
)

REM Verify MySQL is accessible
echo [INFO] Verifying MySQL connection...
podman exec %MYSQL_CONTAINER% mysqladmin ping -h localhost -uroot -pCainiao@123 >nul 2>&1
if errorlevel 1 (
    echo [WARN] MySQL may not be fully ready yet. Continuing anyway...
) else (
    echo [OK] MySQL is accessible.
)

REM ============================================================
REM Step 3: Start Nginx
REM ============================================================
echo.
echo [3/5] Checking Nginx...

REM Check if port 80 is already in use by nginx
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr /C:":80 " ^| findstr /C:"LISTENING"') do (
    echo [OK] Nginx is already running on port 80.
    goto :nginx_done
)

echo [INFO] Starting Nginx...
start "" "%NGINX_EXE%" -p "%NGINX_DIR%" -c "%NGINX_DIR%\conf\nginx.conf"
timeout /t 3 /nobreak >nul

REM Verify Nginx started
netstat -ano 2>nul | findstr /C:":80 " | findstr /C:"LISTENING" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to start Nginx.
    echo [INFO] Check logs: %NGINX_DIR%\logs\error.log
    pause
    exit /b 1
) else (
    echo [OK] Nginx started on port 80.
)

:nginx_done

REM ============================================================
REM Step 4: Start Backend (FastAPI)
REM ============================================================
echo.
echo [4/5] Checking Backend (FastAPI on port 8000)...

REM Test if port 8000 is already in use (backend running)
curl -s -o nul -w "" http://localhost:8000/docs >nul 2>&1
if not errorlevel 1 (
    echo [OK] Backend is already running.
) else (
    echo [INFO] Starting Backend server...

    REM Set USERNAME env var (required by pymysql in Git Bash context)
    for /f "tokens=2 delims==" %%I in ('wmic os get csname /value 2^>nul') do set "USERNAME=%%I"
    if not defined USERNAME set "USERNAME=%USERNAME%"

    start "" cmd /c "cd /d %BACKEND_DIR% && set USERNAME=%USERNAME% && "%PYTHON_EXE%" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    echo [INFO] Waiting for Backend to initialize...
    timeout /t 6 /nobreak >nul

    curl -s -o nul -w "" http://localhost:8000/docs >nul 2>&1
    if errorlevel 1 (
        echo [WARN] Backend may not be fully ready yet. Check console for errors.
    ) else (
        echo [OK] Backend is running on port 8000.
    )
)

REM ============================================================
REM Step 5: Start Frontend (Vue3 Dev Server)
REM ============================================================
echo.
echo [5/5] Checking Frontend (Vue3 on port 5173)...

curl -s -o nul -w "" http://localhost:5173 >nul 2>&1
if not errorlevel 1 (
    echo [OK] Frontend is already running.
) else (
    echo [INFO] Starting Frontend dev server...
    set "PATH=%NODE_DIR%;%PATH%"
    set "NODE_OPTIONS="
    start "" cmd /c "cd /d %FRONTEND_DIR% && set NODE_OPTIONS= && call npm.cmd run dev"
    echo [INFO] Waiting for Frontend to initialize...
    timeout /t 6 /nobreak >nul

    curl -s -o nul -w "" http://localhost:5173 >nul 2>&1
    if errorlevel 1 (
        echo [WARN] Frontend may not be fully ready yet.
    ) else (
        echo [OK] Frontend is running on port 5173.
    )
)

REM ============================================================
REM Summary
REM ============================================================
echo.
echo ============================================================
echo   All services started!
echo ============================================================
echo.
echo   Access Points:
echo   - Main Site:   http://localhost
echo   - API:         http://localhost:8000
echo   - API Docs:    http://localhost:8000/docs
echo   - Frontend:    http://localhost:5173
echo.
echo   Press any key to open browser...
pause >nul

start http://localhost
echo.
echo [OK] Cainiao Design is running!
echo.
pause
