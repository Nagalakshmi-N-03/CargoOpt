@echo off
title CargoOpt Frontend Server
echo ========================================
echo    CargoOpt Frontend Startup Script
echo ========================================
echo.

:: Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

:: Check if npm is available
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: npm is not available
    echo Please check your Node.js installation
    pause
    exit /b 1
)

:: Navigate to frontend directory
cd /d "%~dp0..\frontend"

:: Check if package.json exists
if not exist "package.json" (
    echo ERROR: package.json not found in frontend directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

:: Check if node_modules exists, if not install dependencies
if not exist "node_modules" (
    echo Installing dependencies...
    echo This may take a few minutes...
    npm install
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo Dependencies installed successfully!
    echo.
)

:: Check for environment file
if not exist ".env" (
    echo Creating default environment file...
    (
        echo REACT_APP_API_URL=http://localhost:8000/api
        echo REACT_APP_VERSION=1.0.0
        echo REACT_APP_ENVIRONMENT=development
        echo GENERATE_SOURCEMAP=false
    ) > .env
    echo Environment file created!
    echo.
)

:: Display configuration
echo ========================================
echo        Frontend Configuration
echo ========================================
echo API URL: http://localhost:3000
echo Backend API: http://localhost:8000/api
echo Environment: development
echo.

:: Ask user if they want to build first
set /p BUILD_OPTION="Do you want to build the project first? (y/N): "
if /i "%BUILD_OPTION%"=="y" (
    echo Building project...
    npm run build
    if %errorlevel% neq 0 (
        echo ERROR: Build failed
        pause
        exit /b 1
    )
    echo Build completed successfully!
    echo.
)

:: Start the development server
echo ========================================
echo    Starting CargoOpt Frontend Server
echo ========================================
echo.
echo The application will open in your browser shortly...
echo.
echo Press Ctrl+C to stop the server
echo.

:: Start the development server
npm start

:: If we get here, the server was stopped
echo.
echo ========================================
echo    CargoOpt Frontend Server Stopped
echo ========================================
echo.
pause