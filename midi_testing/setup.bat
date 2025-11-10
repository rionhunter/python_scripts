@echo off
echo MIDI Testing Suite Setup
echo ========================
echo.

echo Installing Python dependencies...
pip install python-rtmidi>=1.4.9 mido>=1.2.10 pygame>=2.1.0 colorama>=0.4.4 psutil>=5.9.0

echo.
echo Setup complete! You can now run the MIDI testing suite:
echo   python midi_test_suite.py
echo.
pause