@echo off
REM ============================================
REM Frontend Development Server Startup Script
REM ============================================

setlocal enabledelayedexpansion

echo ============================================
echo Starting Frontend Development Server
echo ============================================
echo.

REM Set project root directory
set "PROJECT_ROOT=%~dp0.."
set "FRONTEND_DIR=%PROJECT_ROOT%\frontend"

REM Check if frontend directory exists
if not exist "%FRONTEND_DIR%" (
    echo [ERROR] Frontend directory not found at %FRONTEND_DIR%
    pause
    exit /b 1
)

cd /d "%FRONTEND_DIR%"

REM Check if Node.js is installed
where node >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Display Node.js version
for /f "tokens=*" %%i in ('node --version') do set "NODE_VERSION=%%i"
for /f "tokens=*" %%i in ('npm --version') do set "NPM_VERSION=%%i"
echo [INFO] Node.js version: %NODE_VERSION%
echo [INFO] npm version: %NPM_VERSION%

REM Check if node_modules exists
if not exist "node_modules" (
    echo [WARNING] node_modules not found. Installing dependencies...
    call npm install
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
)

REM Check if package.json exists
if not exist "package.json" (
    echo [ERROR] package.json not found in frontend directory!
    pause
    exit /b 1
)

REM Load environment variables
if exist ".env.local" (
    echo [INFO] Loading .env.local...
    for /f "usebackq tokens=1,* delims==" %%a in (".env.local") do (
        set "line=%%a"
        if not "!line:~0,1!"=="#" (
            if not "%%a"=="" set "%%a=%%b"
        )
    )
)

REM Set default environment variables
if not defined REACT_APP_API_URL set "REACT_APP_API_URL=http://localhost:8000"
if not defined PORT set "PORT=3000"
if not defined BROWSER set "BROWSER=none"

echo.
echo ============================================
echo Frontend Configuration:
echo   Port: %PORT%
echo   API URL: %REACT_APP_API_URL%
echo ============================================
echo.

REM Detect package manager and framework
set "START_CMD=npm start"

if exist "yarn.lock" (
    where yarn >nul 2>nul
    if not errorlevel 1 (
        set "START_CMD=yarn start"
        echo [INFO] Using Yarn package manager
    )
)

if exist "pnpm-lock.yaml" (
    where pnpm >nul 2>nul
    if not errorlevel 1 (
        set "START_CMD=pnpm start"
        echo [INFO] Using pnpm package manager
    )
)

REM Check for Vite configuration
if exist "vite.config.js" (
    set "START_CMD=npm run dev"
    echo [INFO] Detected Vite project
) else if exist "vite.config.ts" (
    set "START_CMD=npm run dev"
    echo [INFO] Detected Vite project
)

REM Check for Next.js
if exist "next.config.js" (
    set "START_CMD=npm run dev"
    echo [INFO] Detected Next.js project
) else if exist "next.config.mjs" (
    set "START_CMD=npm run dev"
    echo [INFO] Detected Next.js project
)

echo.
echo [INFO] Starting frontend server with: %START_CMD%
echo [INFO] Press Ctrl+C to stop the server
echo.

REM Start the development server
%START_CMD%

if errorlevel 1 (
    echo.
    echo [ERROR] Frontend server exited with an error.
    pause
    exit /b 1
)

echo.
echo [INFO] Frontend server stopped.
pause