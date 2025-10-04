@echo off
REM CargoOpt Backend Startup Script for Windows
REM Starts the FastAPI backend server

echo.
echo ========================================
echo    CargoOpt Backend Startup
echo ========================================
echo.

REM Add PostgreSQL 18 to PATH
set "PATH=%PATH%;C:\Program Files\PostgreSQL\18\bin"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "..\venv\" (
    echo Virtual environment not found. Creating one...
    python -m venv ..\venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call ..\venv\Scripts\activate.bat

REM Check if requirements are installed
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo Installing requirements...
    pip install -r ..\requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install requirements
        pause
        exit /b 1
    )
)

REM Check if .env file exists
if not exist "..\.env" (
    echo WARNING: .env file not found!
    echo Please create .env file from .env.example
    echo Continuing with default settings...
)

REM Create necessary directories
echo Creating necessary directories...
if not exist "..\logs" mkdir "..\logs"
if not exist "..\data\exports" mkdir "..\data\exports"
if not exist "..\data\exports\stowage_plans" mkdir "..\data\exports\stowage_plans"
if not exist "..\data\exports\reports" mkdir "..\data\exports\reports"
if not exist "..\data\temp" mkdir "..\data\temp"

REM Set environment variables
set PYTHONPATH=..
set CARGOOPT_ENV=development

REM Display startup information
echo.
echo ========================================
echo    Starting CargoOpt Backend Server
echo ========================================
echo.
echo Backend URL: http://localhost:5000
echo API Docs:    http://localhost:5000/docs
echo Health Check: http://localhost:5000/health
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the FastAPI server
cd ..
python run.py

REM Deactivate virtual environment on exit
call venv\Scripts\deactivate.bat

pause