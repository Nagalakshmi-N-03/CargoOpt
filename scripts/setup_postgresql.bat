@echo off
REM CargoOpt PostgreSQL Setup Script for Windows - PostgreSQL 18

echo.
echo ========================================
echo    CargoOpt PostgreSQL Setup - PG18
echo ========================================
echo.

setlocal enabledelayedexpansion

REM Add PostgreSQL 18 to PATH
set "PG_PATH=C:\Program Files\PostgreSQL\18\bin"
set "PATH=%PATH%;%PG_PATH%"

REM Check if PostgreSQL is installed
echo Checking PostgreSQL installation...
"%PG_PATH%\psql.exe" --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: PostgreSQL 18 is not installed at %PG_PATH%
    echo.
    echo Please install PostgreSQL 18 from: https://www.postgresql.org/download/windows/
    echo.
    pause
    exit /b 1
)

echo Found PostgreSQL 18

REM Check if PostgreSQL service is running
echo Checking PostgreSQL service...
sc query postgresql-x64-18 | find "RUNNING" >nul
if errorlevel 1 (
    echo WARNING: PostgreSQL service is not running
    echo Attempting to start PostgreSQL service...
    
    net start postgresql-x64-18 >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Could not start PostgreSQL service
        echo Please start PostgreSQL service manually and run this script again
        echo.
        echo You can start it from Services.msc or run:
        echo net start postgresql-x64-18
        pause
        exit /b 1
    )
    echo PostgreSQL service started successfully
)

REM Set default connection parameters
set DB_HOST=localhost
set DB_PORT=5432
set DB_NAME=cargoopt
set DB_USER=cargoopt_user
set DB_PASSWORD=cargoopt_password

REM Test basic PostgreSQL connection
echo Testing PostgreSQL connection...
set PGPASSWORD=postgres
"%PG_PATH%\psql.exe" -h %DB_HOST% -p %DB_PORT% -U postgres -c "SELECT version();" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Cannot connect to PostgreSQL as 'postgres' user
    echo.
    echo Please ensure password is correct in this script (line: set PGPASSWORD=postgres)
    echo.
    pause
    exit /b 1
)

echo Successfully connected to PostgreSQL!

REM Create database user
echo Creating database user '%DB_USER%'...
"%PG_PATH%\psql.exe" -h %DB_HOST% -p %DB_PORT% -U postgres -c "CREATE USER %DB_USER% WITH PASSWORD '%DB_PASSWORD%';" >nul 2>&1
if errorlevel 1 (
    echo User already exists or cannot be created, continuing...
)

REM Create database
echo Creating database '%DB_NAME%'...
"%PG_PATH%\psql.exe" -h %DB_HOST% -p %DB_PORT% -U postgres -c "CREATE DATABASE %DB_NAME% WITH OWNER %DB_USER%;" >nul 2>&1
if errorlevel 1 (
    echo Database already exists or cannot be created, continuing...
)

REM Create .env file
echo Creating .env file...
(
echo DATABASE_URL=postgresql://%DB_USER%:%DB_PASSWORD%@%DB_HOST%:%DB_PORT%/%DB_NAME%
echo DATABASE_NAME=%DB_NAME%
echo DATABASE_USER=%DB_USER%
echo DATABASE_PASSWORD=%DB_PASSWORD%
echo DATABASE_HOST=%DB_HOST%
echo DATABASE_PORT=%DB_PORT%
echo APP_ENV=development
echo DEBUG=True
echo SECRET_KEY=your-secret-key-change-in-production
echo HOST=0.0.0.0
echo PORT=5000
echo API_V1_PREFIX=/api/v1
) > ..\.env

echo .env file created successfully!

REM Initialize database schema
echo.
echo ========================================
echo    Initializing Database Schema
echo ========================================
echo.

echo Running database initialization...
cd ..
python setup_database.py
cd scripts

echo.
echo ========================================
echo    Setup Complete!
echo ========================================
echo.
echo Database has been setup successfully!
echo.
echo You can now: scripts\start_backend.bat
echo Access the API at: http://localhost:5000
echo.
pause