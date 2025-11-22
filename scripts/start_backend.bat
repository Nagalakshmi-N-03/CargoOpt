@echo off
REM ============================================
REM Backend Server Startup Script
REM ============================================

setlocal enabledelayedexpansion

echo ============================================
echo Starting Backend Server
echo ============================================
echo.

REM Set project root directory
set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%"

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run install_dependencies.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found. Using default configuration.
    if exist ".env.example" (
        copy ".env.example" ".env"
        echo [INFO] Created .env from .env.example
    )
)

REM Load environment variables from .env
if exist ".env" (
    echo [INFO] Loading environment variables...
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        set "line=%%a"
        if not "!line:~0,1!"=="#" (
            if not "%%a"=="" set "%%a=%%b"
        )
    )
)

REM Set default values if not defined
if not defined BACKEND_HOST set "BACKEND_HOST=0.0.0.0"
if not defined BACKEND_PORT set "BACKEND_PORT=8000"
if not defined DEBUG set "DEBUG=false"

REM Check if required packages are installed
echo [INFO] Verifying dependencies...
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo [ERROR] FastAPI not installed. Running dependency installation...
    call "%~dp0install_dependencies.bat"
)

REM Check database connection
echo [INFO] Checking database connection...
python -c "from backend.database import check_connection; check_connection()" 2>nul
if errorlevel 1 (
    echo [WARNING] Database connection check failed.
    echo Make sure PostgreSQL is running and configured correctly.
)

echo.
echo ============================================
echo Server Configuration:
echo   Host: %BACKEND_HOST%
echo   Port: %BACKEND_PORT%
echo   Debug: %DEBUG%
echo ============================================
echo.

REM Start the backend server
echo [INFO] Starting uvicorn server...
echo [INFO] Press Ctrl+C to stop the server
echo.

if "%DEBUG%"=="true" (
    python -m uvicorn backend.main:app --host %BACKEND_HOST% --port %BACKEND_PORT% --reload --log-level debug
) else (
    python -m uvicorn backend.main:app --host %BACKEND_HOST% --port %BACKEND_PORT% --workers 4
)

REM Handle exit
if errorlevel 1 (
    echo.
    echo [ERROR] Server exited with an error.
    pause
    exit /b 1
)

echo.
echo [INFO] Server stopped.
pause