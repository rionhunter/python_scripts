"""Launch Dynamic Replacer GUI"""
$scriptPath = Join-Path $PSScriptRoot "..\text_editing\dynamic_replacer.py"
$python = "py"
if (Get-Command $python -ErrorAction SilentlyContinue) {
  & $python $scriptPath
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
  & python $scriptPath
} else {
  Write-Error "Python interpreter not found in PATH. Please install Python or add it to PATH."
  exit 1
}
exit $LASTEXITCODE