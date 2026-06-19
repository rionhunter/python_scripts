<#
Build a Windows distributable for Text File Compiler using PyInstaller.
#>
param(
  [switch]$OneFile
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Definition
$venvDir = Join-Path $Root ".venv"
$pythonExe = Join-Path $venvDir "Scripts\python.exe"

if (-Not (Test-Path $pythonExe)) {
  Write-Host "Creating virtual environment at $venvDir ..."
  & python -m venv $venvDir
}

Write-Host "Installing runtime/build dependencies ..."
& $pythonExe -m pip install --upgrade pip
& $pythonExe -m pip install -r (Join-Path $Root "requirements.txt")
& $pythonExe -m pip install -r (Join-Path $Root "requirements-build.txt")

$buildScript = Join-Path $Root "build_package.py"
if ($OneFile) {
  & $pythonExe $buildScript --onefile
} else {
  & $pythonExe $buildScript
}

Write-Host "Build complete. See dist\TextFileCompiler"
