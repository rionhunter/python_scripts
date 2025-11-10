@echo off
set "SCRIPT=%~dp0..\text_editing\dynamic_replacer.py"
set "PY="
where py >nul 2>nul
if %ERRORLEVEL%==0 (
  set "PY=py"
) else (
  where python >nul 2>nul
  if %ERRORLEVEL%==0 (
    set "PY=python"
  ) else (
    echo Python not found in PATH
    exit /b 1
  )
)
%PY% "%SCRIPT%" --test