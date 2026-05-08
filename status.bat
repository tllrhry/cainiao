@echo off
REM ============================================================
REM  CaiNiao Design - Check Services Status
REM ============================================================

set "NGINX_DIR=D:\cainiao\nginx-install\nginx-1.26.3"
set "MYSQL_CONTAINER=mysql-portal"
set "PODMAN_MACHINE=podman-machine-default"

title Cainiao Design - Status Check

echo.
echo ============================================================
echo   CaiNiao Design - Services Status
echo ============================================================
echo.

REM ============================================================
REM Podman Machine Status
REM ============================================================
echo [Podman Machine - %PODMAN_MACHINE%]
for /f "tokens=*" %%i in ('podman machine inspect %PODMAN_MACHINE% 2^>nul ^| findstr /C:"\"State\":"') do (
    echo   %%i
)
echo.

REM ============================================================
REM MySQL Container Status
REM ============================================================
echo [MySQL Container - %MYSQL_CONTAINER%]
podman ps -a --format "{{.Names}}\t{{.Status}}" 2>nul | findstr /C:"%MYSQL_CONTAINER%" >nul 2>&1
if errorlevel 1 (
    echo   Container: NOT FOUND
) else (
    for /f "tokens=1,2" %%a in ('podman ps -a --format "{{.Names}}@{{.Status}}" 2^>nul ^| findstr /C:"%MYSQL_CONTAINER%@"') do (
        echo   Container: %%a
        echo   Status: %%b
    )
)
echo.

REM ============================================================
REM MySQL Database Connectivity
REM ============================================================
echo [MySQL Database - cainiao_design]
podman exec %MYSQL_CONTAINER% mysqladmin ping -h localhost -uroot -pCainiao@123 >nul 2>&1
if errorlevel 1 (
    echo   Status: NOT CONNECTABLE
) else (
    echo   Status: CONNECTABLE
)
echo.

REM ============================================================
REM Nginx Status
REM ============================================================
echo [Nginx]
powershell -Command "Get-Process -Name 'nginx' -ErrorAction SilentlyContinue | Select-Object Name,Id" 2>nul
if errorlevel 1 (
    echo   Status: NOT RUNNING
) else (
    echo   Status: RUNNING
)
echo   Config: %NGINX_DIR%\conf\nginx.conf
echo.

REM ============================================================
REM Backend (Python/Uvicorn) Status
REM ============================================================
echo [Backend - FastAPI]
curl -s -o nul -w "HTTP Status: %%{http_code}\n" http://localhost:8000/docs >nul 2>&1
if errorlevel 1 (
    echo   Status: NOT RESPONDING
) else (
    echo   Status: RUNNING
)
echo   Endpoint: http://localhost:8000
echo   Docs:     http://localhost:8000/docs
echo.

REM ============================================================
REM Frontend (Node/Vite) Status
REM ============================================================
echo [Frontend - Vue3 Dev Server]
curl -s -o nul -w "HTTP Status: %%{http_code}\n" http://localhost:5173 >nul 2>&1
if errorlevel 1 (
    echo   Status: NOT RESPONDING
) else (
    echo   Status: RUNNING
)
echo   Endpoint: http://localhost:5173
echo.

REM ============================================================
REM Overall Status
REM ============================================================
echo ============================================================
echo   Access Points
echo ============================================================
echo   Main Site:  http://localhost
echo   API:        http://localhost:8000
echo   API Docs:   http://localhost:8000/docs
echo   Frontend:   http://localhost:5173
echo ============================================================
echo.
pause
