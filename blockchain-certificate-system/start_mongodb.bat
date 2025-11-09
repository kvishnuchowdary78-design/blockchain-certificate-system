@echo off
echo ========================================
echo   Starting MongoDB for Windows
echo ========================================
echo.

REM Try to start MongoDB as a service first
echo Attempting to start MongoDB service...
net start MongoDB 2>nul

if %ERRORLEVEL% EQU 0 (
    echo SUCCESS: MongoDB service started!
    echo.
    echo MongoDB is now running on: mongodb://localhost:27017
    echo.
    echo You can now run: python final_fix_solution.py
    pause
    exit /b 0
)

echo.
echo Service start failed. Trying manual start...
echo.

REM Check if MongoDB is installed
if exist "C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe" (
    set MONGODB_PATH=C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe
) else if exist "C:\Program Files\MongoDB\Server\6.0\bin\mongod.exe" (
    set MONGODB_PATH=C:\Program Files\MongoDB\Server\6.0\bin\mongod.exe
) else if exist "C:\Program Files\MongoDB\Server\5.0\bin\mongod.exe" (
    set MONGODB_PATH=C:\Program Files\MongoDB\Server\5.0\bin\mongod.exe
) else (
    echo ERROR: MongoDB not found!
    echo.
    echo Please install MongoDB from:
    echo https://www.mongodb.com/try/download/community
    echo.
    pause
    exit /b 1
)

REM Create data directory
if not exist "C:\data\db" (
    echo Creating data directory...
    mkdir "C:\data\db"
)

echo Starting MongoDB manually...
echo MongoDB Path: %MONGODB_PATH%
echo Data Path: C:\data\db
echo.
echo IMPORTANT: Keep this window open while using the application!
echo.
echo Press CTRL+C to stop MongoDB when done.
echo.

"%MONGODB_PATH%" --dbpath "C:\data\db"