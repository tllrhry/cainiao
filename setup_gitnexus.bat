@ECHO OFF
ECHO ============================================
ECHO GitNexus Setup Script
ECHO ============================================
ECHO.

REM Set Node.js path
SET "NODE_DIR=C:\Users\CNGG\.workbuddy\binaries\node\versions\22.12.0"
SET "PATH=%NODE_DIR%;%PATH%"

REM Step 1: Install gitnexus globally
ECHO [1/3] Installing gitnexus globally...
CALL "%NODE_DIR%\npm.cmd" install -g gitnexus@latest
IF %ERRORLEVEL% NEQ 0 (
    ECHO ERROR: npm install failed with exit code %ERRORLEVEL%
    PAUSE
    EXIT /B %ERRORLEVEL%
)
ECHO Installation complete.
ECHO.

REM Step 2: Run gitnexus analyze
ECHO [2/3] Running gitnexus analyze in D:\cainiao...
CD /D D:\cainiao
CALL gitnexus analyze --force
IF %ERRORLEVEL% NEQ 0 (
    ECHO WARNING: gitnexus analyze exited with code %ERRORLEVEL%
)
ECHO.

REM Step 3: Run gitnexus setup
ECHO [3/3] Running gitnexus setup for MCP auto-configuration...
CALL gitnexus setup
IF %ERRORLEVEL% NEQ 0 (
    ECHO WARNING: gitnexus setup exited with code %ERRORLEVEL%
)
ECHO.

ECHO ============================================
ECHO GitNexus setup complete!
ECHO ============================================
PAUSE
