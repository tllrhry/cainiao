@ECHO OFF
SET "NODE_DIR=C:\Users\CNGG\.workbuddy\binaries\node\versions\22.12.0"
SET "PATH=%NODE_DIR%;%PATH%"
CD /D D:\cainiao
CALL gitnexus analyze --force
