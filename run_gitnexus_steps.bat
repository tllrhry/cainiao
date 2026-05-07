@ECHO OFF
SET "NODE_DIR=C:\Users\CNGG\.workbuddy\binaries\node\versions\22.12.0"
SET "PATH=%NODE_DIR%;%PATH%"

ECHO ============================================
ECHO Step 1: Installing gitnexus globally
ECHO ============================================
CALL "%NODE_DIR%\npm.cmd" install -g gitnexus@latest
ECHO Exit code: %ERRORLEVEL%
ECHO.

ECHO ============================================
ECHO Step 2: Running gitnexus analyze --force
ECHO ============================================
CD /D D:\cainiao
CALL gitnexus analyze --force
ECHO Exit code: %ERRORLEVEL%
ECHO.

ECHO ============================================
ECHO Step 3: Running gitnexus setup
ECHO ============================================
CALL gitnexus setup
ECHO Exit code: %ERRORLEVEL%
ECHO.

ECHO ============================================
ECHO All steps complete
ECHO ============================================
