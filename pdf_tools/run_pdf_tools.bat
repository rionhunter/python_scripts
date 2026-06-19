@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "PY_EXE=C:\Python313\python.exe"

if exist "%PY_EXE%" (
    "%PY_EXE%" "%SCRIPT_DIR%pdf_tui.py" %*
) else (
    python "%SCRIPT_DIR%pdf_tui.py" %*
)
endlocal
