@echo off
echo Starting Cainiao Design backend...

set PY=C:\Users\CNGG\.workbuddy\binaries\python\envs\cainiao\Scripts\python.exe
cd /d D:\cainiao\backend

"%PY%" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause
