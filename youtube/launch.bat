@echo off
REM Check if the virtual environment exists
if not exist "yt_audio_env\Scripts\activate" (
    echo Virtual environment not found. Please run the setup.bat script first.
    pause
    exit /b 1
)

REM Activate the virtual environment
echo Activating virtual environment...
call yt_audio_env\Scripts\activate

REM Run the Python script
echo Running Python script...
python audio_snippet.py

REM Deactivate the virtual environment
deactivate

echo Script execution complete.
pause
