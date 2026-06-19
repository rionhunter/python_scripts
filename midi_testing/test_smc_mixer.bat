@echo off
echo SMC-Mixer-bt MIDI Device Troubleshooter
echo ========================================
echo.

cd /d "%~dp0"

echo Testing your SMC-Mixer-bt device...
python test_smc_mixer.py

echo.
echo If the test didn't work, try running as Administrator:
echo 1. Right-click on this batch file
echo 2. Select "Run as administrator"
echo 3. Try again

pause