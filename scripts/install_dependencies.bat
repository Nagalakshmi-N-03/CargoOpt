@echo off
title CargoOpt Dependencies Installation
echo ========================================
echo    CargoOpt Dependencies Installer
echo ========================================
echo.

:: Backend dependencies
echo Installing Backend Dependencies...
cd /d "%~dp0..\backend"

python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo ✅ Backend dependencies installed successfully!
) else (
    echo ❌ Backend dependencies installation failed!
    pause
    exit /b 1
)

:: Frontend dependencies  
echo.
echo Installing Frontend Dependencies...
cd /d "%~dp0..\frontend"

npm install

if %errorlevel% equ 0 (
    echo ✅ Frontend dependencies installed successfully!
) else (
    echo ❌ Frontend dependencies installation failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo    All Dependencies Installed!
echo ========================================
echo.
echo You can now start the application:
echo.
echo Backend: scripts\start_backend.bat
echo Frontend: scripts\start_frontend.bat
echo.
pause