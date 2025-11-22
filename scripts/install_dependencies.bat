@echo off
REM ============================================
REM Dependencies Installation Script
REM ============================================

setlocal enabledelayedexpansion

echo ============================================
echo Installing Project Dependencies
echo ============================================
echo.

REM Set project root directory
set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%"

REM ============================================
REM Python Backend Dependencies
REM ============================================
echo [STEP 1/4] Checking Python installation...

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.9+ from https://python.org/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set "PYTHON_VERSION=%%i"
echo [INFO] Found %PYTHON_VERSION%

REM Check Python version is 3.9+
python -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" 2>nul
if errorlevel 1 (
    echo [ERROR] Python 3.9 or higher is required.
    pause
    exit /b 1
)

echo.
echo [STEP 2/4] Setting up Python virtual environment...

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [INFO] Virtual environment created successfully.
) else (
    echo [INFO] Virtual environment already exists.
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install Python dependencies
echo.
echo [STEP 3/4] Installing Python dependencies...

if exist "requirements.txt" (
    echo [INFO] Installing from requirements.txt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install Python dependencies.
        pause
        exit /b 1
    )
) else if exist "pyproject.toml" (
    echo [INFO] Installing from pyproject.toml...
    pip install -e .
    if errorlevel 1 (
        echo [ERROR] Failed to install Python dependencies.
        pause
        exit /b 1
    )
) else (
    echo [WARNING] No requirements.txt or pyproject.toml found.
    echo [INFO] Installing common backend dependencies...
    pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv pydantic alembic python-multipart
)

REM Install dev dependencies if they exist
if exist "requirements-dev.txt" (
    echo [INFO] Installing development dependencies...
    pip install -r requirements-dev.txt
)

echo [INFO] Python dependencies installed successfully.

REM ============================================
REM Node.js Frontend Dependencies
REM ============================================
echo.
echo [STEP 4/4] Installing frontend dependencies...

set "FRONTEND_DIR=%PROJECT_ROOT%\frontend"

if not exist "%FRONTEND_DIR%" (
    echo [INFO] No frontend directory found. Skipping frontend dependencies.
    goto :FINISH
)

cd /d "%FRONTEND_DIR%"

where node >nul 2>nul
if errorlevel 1 (
    echo [WARNING] Node.js is not installed. Skipping frontend dependencies.
    echo [INFO] Install Node.js from https://nodejs.org/ for frontend support.
    goto :FINISH
)

for /f "tokens=*" %%i in ('node --version') do set "NODE_VERSION=%%i"
echo [INFO] Found Node.js %NODE_VERSION%

if not exist "package.json" (
    echo [WARNING] No package.json found in frontend directory.
    goto :FINISH
)

REM Detect and use appropriate package manager
if exist "pnpm-lock.yaml" (
    where pnpm >nul 2>nul
    if not errorlevel 1 (
        echo [INFO] Installing with pnpm...
        pnpm install
        goto :FRONTEND_DONE
    )
)

if exist "yarn.lock" (
    where yarn >nul 2>nul
    if not errorlevel 1 (
        echo [INFO] Installing with yarn...
        yarn install
        goto :FRONTEND_DONE
    )
)

echo [INFO] Installing with npm...
npm install

:FRONTEND_DONE
if errorlevel 1 (
    echo [ERROR] Failed to install frontend dependencies.
    pause
    exit /b 1
)

echo [INFO] Frontend dependencies installed successfully.

:FINISH
cd /d "%PROJECT_ROOT%"

echo.
echo ============================================
echo Installation Complete!
echo ============================================
echo.
echo Next steps:
echo   1. Configure your .env file
echo   2. Run setup_postgresql.bat to configure database
echo   3. Run start_backend.bat to start the API server
echo   4. Run start_frontend.bat to start the frontend
echo.
pause