# Requires PowerShell 5+ or PowerShell 7+
# === XenberSDU Automated Setup & Launch (Windows) ===

Write-Host ">>> Starting XenberSDU setup..." -ForegroundColor Cyan

# --- Project root
$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Definition)
Write-Host "Project folder: $projectRoot" -ForegroundColor Green

# --- Allow scripts
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# --- Detect Python 3.11
$pythonPath = ""
$pythonCheck = & python --version 2>&1
if ($pythonCheck -match "Python 3\.11") {
    $pythonPath = "python"
} else {
    Write-Host "❌ Python 3.11 not found!" -ForegroundColor Red
    Write-Host "Install it from https://www.python.org/downloads/release/python-3117/" -ForegroundColor Yellow
    exit 1
}
Write-Host "Using Python: $pythonCheck" -ForegroundColor Green

# --- Create virtual environment
$venvPath = Join-Path $projectRoot "venv"
if (!(Test-Path $venvPath)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    & $pythonPath -m venv $venvPath
} else {
    Write-Host "Virtual environment already exists." -ForegroundColor Green
}

# --- Activate venv
$activatePath = Join-Path $venvPath "Scripts\Activate.ps1"
Write-Host "Activating virtual environment..."
& $activatePath

# --- Install dependencies
$reqPath = Join-Path $projectRoot "requirements.txt"
if (Test-Path $reqPath) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install --upgrade pip setuptools wheel
    pip install -r $reqPath
} else {
    Write-Host "requirements.txt not found. Skipping installation." -ForegroundColor Red
}

# --- Launch backend in a new window
$backendCmd = "& `"$activatePath`"; python -m uvicorn backend.api:app --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command $backendCmd" -WorkingDirectory $projectRoot

# --- Launch frontend in a new window
$frontendPath = Join-Path $projectRoot "frontend"
$frontendCmd = "& `"$activatePath`"; python -m streamlit run dashboard.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command $frontendCmd" -WorkingDirectory $frontendPath

Write-Host ">>> Setup complete!" -ForegroundColor Green
Write-Host "Backend → http://127.0.0.1:8000"
Write-Host "Frontend → http://localhost:8501"
