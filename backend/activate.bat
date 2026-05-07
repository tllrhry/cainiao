@echo off
set "VENV=C:\Users\CNGG\.workbuddy\binaries\python\envs\cainiao"
set "PATH=%VENV%\Scripts;%VENV%;%PATH%"
echo ==========================================
echo   Cainiao Design - Python venv activated
echo ==========================================
echo   Python: %VENV%\Scripts\python.exe
python --version
echo.
echo   Now you can use 'python' directly:
echo     python test_auth.py
echo     python -m uvicorn app.main:app --reload
echo ==========================================
cmd /k
