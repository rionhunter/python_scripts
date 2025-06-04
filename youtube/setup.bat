@echo off
REM Check if Python is installed
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python is not installed. Please install Python and try again.
    pause
    exit /b 1
)

REM Create a virtual environment
echo Creating virtual environment...
python -m venv yt_audio_env

REM Activate the virtual environment
echo Activating virtual environment...
call yt_audio_env\Scripts\activate

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install necessary libraries
echo Installing necessary libraries...
pip install pytube moviepy pydub tk

REM Deactivate the virtual environment
deactivate

echo Virtual environment setup is complete.
pause
