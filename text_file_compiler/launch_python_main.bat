@echo off
setlocal

set "ROOT=%~dp0"
set "PYTHON_EXE=%ROOT%.venv\Scripts\python.exe"

if exist "%PYTHON_EXE%" (
	"%PYTHON_EXE%" "%ROOT%main.py" %*
) else (
	python "%ROOT%main.py" %*
)

pause