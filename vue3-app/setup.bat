@echo off
set NODE_DIR=C:\Users\CNGG\.workbuddy\binaries\node\versions\22.12.0
set "PATH=%NODE_DIR%;%PATH%"
cd /d D:\cainiao\vue3-app
echo Installing dependencies...
npm install
echo.
echo Done! Run dev.bat to start dev server.
pause
