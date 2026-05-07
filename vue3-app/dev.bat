@echo off
set NODE_DIR=C:\Users\CNGG\.workbuddy\binaries\node\versions\22.12.0
set "PATH=%NODE_DIR%;%PATH%"
cd /d D:\cainiao\vue3-app
echo Starting Vue 3 dev server...
echo Open http://localhost:5173 in your browser.
npm run dev
pause
