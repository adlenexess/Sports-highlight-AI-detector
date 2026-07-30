# Start the SportsLab <-> AI detector integration gateway
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$VenvPython = Join-Path $Root "backend\algorithm\.venv\Scripts\python.exe"
$Requirements = Join-Path $Root "backend\algorithm\AI-Powered-highlight-detector-main\requirements.txt"

if (Test-Path $VenvPython) {
    $Python = $VenvPython
    $Pip = Join-Path $Root "backend\algorithm\.venv\Scripts\pip.exe"
    $PythonArgs = @()
} else {
    $Python = "py"
    $PythonArgs = @("-3")
    $Pip = "py"
    Write-Host "Note: no venv found. Using system Python (py -3)."
}

$check = & $Python @PythonArgs -c "import flask, moviepy" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing Python dependencies (first run may take a few minutes)..."
    if (Test-Path $Pip) {
        & $Pip install -r $Requirements Flask
    } else {
        & py -3 -m pip install -r $Requirements Flask
    }
}

Set-Location $Root
& $Python @PythonArgs (Join-Path $PSScriptRoot "gateway.py")
