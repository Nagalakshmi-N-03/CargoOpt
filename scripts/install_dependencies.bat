@echo off
chcp 65001 >nul
echo ========================================
echo    CargoOpt Dependencies Installer
echo ========================================
echo.

echo Installing Backend Dependencies...
pip install --upgrade pip
pip install setuptools wheel
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Backend dependencies installation failed!
    pause
    exit /b 1
)

echo.
echo ✅ Backend dependencies installed successfully!
echo.

echo Installing Frontend Dependencies...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo ❌ Frontend dependencies installation failed!
    pause
    exit /b 1
)

echo.
echo ✅ Frontend dependencies installed successfully!
echo.
echo 🎉 All dependencies installed successfully!
pause