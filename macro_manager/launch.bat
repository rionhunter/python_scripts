@echo off
echo ====================================
echo   Macro Manager Launcher
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo Python found!
echo.

REM Check if requirements are installed
echo Checking dependencies...
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Dependencies not found. Installing...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    echo Dependencies OK!
)

echo.
echo Starting Macro Manager...
echo.

REM Launch the application
python macro_manager.py

if errorlevel 1 (
    echo.
    echo ERROR: Application crashed or failed to start
    pause
)
