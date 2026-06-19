<#
Launch script for the Python text_file_compiler application.
- Creates/uses a local virtual environment at .venv
- Installs dependencies from requirements.txt
- Launches the configured entry point (default: main.py)
#>
param(
  [string]$EntryPoint = "main.py",
  [string[]]$ProgramArgs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Definition
$venvDir = Join-Path $Root ".venv"

try {
  if (-Not (Test-Path $venvDir)) {
    Write-Host "Creating virtual environment at $venvDir ..."
    & python -m venv $venvDir
  }

  $pythonExe = Join-Path $venvDir "Scripts\python.exe"
  if (-Not (Test-Path $pythonExe)) {
    Write-Host "Python executable not found in venv, trying system Python..."
    $pythonExe = "python"
  }

  $requirementsPath = Join-Path $Root "requirements.txt"
  if (Test-Path $requirementsPath) {
    Write-Host "Installing dependencies from requirements.txt ..."
    & $pythonExe -m pip install --upgrade pip
    & $pythonExe -m pip install -r $requirementsPath
  }

  $entryPath = Join-Path $Root $EntryPoint
  if (-Not (Test-Path $entryPath)) {
    Write-Host "Entry point not found: $entryPath"
    exit 1
  }

  Write-Host "Launching application: $entryPath"
  & $pythonExe $entryPath @ProgramArgs
} catch {
  Write-Error $_
  exit 1
}