@echo off
REM Wrapper to launch set_global_env_gui.py with administrative privileges on Windows.

:: Check for administrative rights; if not, relaunch with elevation
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrative privileges...
    powershell -Command "Start-Process -Verb runAs -FilePath '%~f0'"
    exit /b
)

REM Running as admin: invoke the Python GUI script
python "%~dp0set_global_env_gui.py"