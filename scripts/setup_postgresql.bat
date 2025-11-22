@echo off
REM ============================================
REM PostgreSQL Database Setup Script
REM ============================================

setlocal enabledelayedexpansion

echo ============================================
echo PostgreSQL Database Setup
echo ============================================
echo.

REM Set project root directory
set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%"

REM Default database configuration
set "DB_HOST=localhost"
set "DB_PORT=5432"
set "DB_NAME=app_database"
set "DB_USER=app_user"
set "DB_PASSWORD="
set "POSTGRES_USER=postgres"

REM Load from .env if exists
if exist ".env" (
    echo [INFO] Loading configuration from .env...
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        set "line=%%a"
        if not "!line:~0,1!"=="#" (
            if "%%a"=="DB_HOST" set "DB_HOST=%%b"
            if "%%a"=="DB_PORT" set "DB_PORT=%%b"
            if "%%a"=="DB_NAME" set "DB_NAME=%%b"
            if "%%a"=="DB_USER" set "DB_USER=%%b"
            if "%%a"=="DB_PASSWORD" set "DB_PASSWORD=%%b"
            if "%%a"=="DATABASE_URL" set "DATABASE_URL=%%b"
        )
    )
)

REM Check for psql
where psql >nul 2>nul
if errorlevel 1 (
    echo [ERROR] PostgreSQL client (psql) not found in PATH!
    echo.
    echo Please ensure PostgreSQL is installed and added to PATH.
    echo Common installation paths:
    echo   - C:\Program Files\PostgreSQL\16\bin
    echo   - C:\Program Files\PostgreSQL\15\bin
    echo.
    echo You can add it to PATH or run this script from PostgreSQL command prompt.
    pause
    exit /b 1
)

echo [INFO] PostgreSQL client found.
echo.

REM Prompt for postgres superuser password
echo Please enter the PostgreSQL superuser (postgres) password:
set /p "PGPASSWORD=Password: "
echo.

REM Test connection
echo [INFO] Testing PostgreSQL connection...
psql -h %DB_HOST% -p %DB_PORT% -U %POSTGRES_USER% -c "SELECT version();" >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Cannot connect to PostgreSQL server.
    echo Please check:
    echo   - PostgreSQL service is running
    echo   - Host: %DB_HOST%
    echo   - Port: %DB_PORT%
    echo   - Password is correct
    pause
    exit /b 1
)
echo [INFO] Connection successful!
echo.

REM Generate password if not set
if "%DB_PASSWORD%"=="" (
    echo [INFO] Generating random password for database user...
    for /f %%i in ('powershell -command "[System.Web.Security.Membership]::GeneratePassword(16,2)"') do set "DB_PASSWORD=%%i"
)

echo ============================================
echo Database Configuration:
echo   Host: %DB_HOST%
echo   Port: %DB_PORT%
echo   Database: %DB_NAME%
echo   User: %DB_USER%
echo ============================================
echo.

REM Create database user
echo [STEP 1/4] Creating database user '%DB_USER%'...
psql -h %DB_HOST% -p %DB_PORT% -U %POSTGRES_USER% -c "DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '%DB_USER%') THEN CREATE ROLE %DB_USER% WITH LOGIN PASSWORD '%DB_PASSWORD%'; END IF; END $$;"
if errorlevel 1 (
    echo [WARNING] Could not create user. It may already exist.
) else (
    echo [INFO] User created successfully.
)

REM Create database
echo.
echo [STEP 2/4] Creating database '%DB_NAME%'...
psql -h %DB_HOST% -p %DB_PORT% -U %POSTGRES_USER% -c "SELECT 1 FROM pg_database WHERE datname = '%DB_NAME%'" | findstr "1" >nul
if errorlevel 1 (
    psql -h %DB_HOST% -p %DB_PORT% -U %POSTGRES_USER% -c "CREATE DATABASE %DB_NAME% OWNER %DB_USER%;"
    echo [INFO] Database created successfully.
) else (
    echo [INFO] Database already exists.
)

REM Grant privileges
echo.
echo [STEP 3/4] Granting privileges...
psql -h %DB_HOST% -p %DB_PORT% -U %POSTGRES_USER% -c "GRANT ALL PRIVILEGES ON DATABASE %DB_NAME% TO %DB_USER%;"
psql -h %DB_HOST% -p %DB_PORT% -U %POSTGRES_USER% -d %DB_NAME% -c "GRANT ALL ON SCHEMA public TO %DB_USER%;"
echo [INFO] Privileges granted.

REM Update .env file
echo.
echo [STEP 4/4] Updating .env file...
set "DATABASE_URL=postgresql://%DB_USER%:%DB_PASSWORD%@%DB_HOST%:%DB_PORT%/%DB_NAME%"

if exist ".env" (
    REM Backup existing .env
    copy ".env" ".env.backup" >nul
    echo [INFO] Backed up existing .env to .env.backup
)

REM Create or update .env
(
    echo # Database Configuration
    echo DB_HOST=%DB_HOST%
    echo DB_PORT=%DB_PORT%
    echo DB_NAME=%DB_NAME%
    echo DB_USER=%DB_USER%
    echo DB_PASSWORD=%DB_PASSWORD%
    echo DATABASE_URL=%DATABASE_URL%
    echo.
    echo # Backend Configuration
    echo BACKEND_HOST=0.0.0.0
    echo BACKEND_PORT=8000
    echo DEBUG=false
    echo.
    echo # Frontend Configuration
    echo REACT_APP_API_URL=http://localhost:8000
) > ".env.new"

if exist ".env" (
    echo [INFO] Merging with existing .env...
    type ".env" >> ".env.new"
)

move /y ".env.new" ".env" >nul
echo [INFO] .env file updated.

REM Run migrations if available
echo.
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    
    if exist "alembic.ini" (
        echo [INFO] Running database migrations with Alembic...
        alembic upgrade head
        if errorlevel 1 (
            echo [WARNING] Migration failed. You may need to run manually.
        ) else (
            echo [INFO] Migrations completed successfully.
        )
    ) else if exist "backend\database.py" (
        echo [INFO] Initializing database tables...
        python -c "from backend.database import init_db; init_db()"
    )
)

echo.
echo ============================================
echo PostgreSQL Setup Complete!
echo ============================================
echo.
echo Database URL: %DATABASE_URL%
echo.
echo Connection details saved to .env file.
echo.
echo To connect manually:
echo   psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME%
echo.
pause