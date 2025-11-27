# Requires PowerShell 5+ or PowerShell 7+
Write-Host ">>> Starting XenberSDU setup..." -ForegroundColor Cyan

# 1. Project root = parent of the setup folder
$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Definition)

# Quote the path to handle spaces
Set-Location "$projectRoot"
Write-Host "Project folder: $projectRoot" -ForegroundColor Green

# 2. Allow scripts to run in this session
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# 3. Create virtual environment if missing
if (!(Test-Path "./venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
} else {
    Write-Host "Virtual environment already exists." -ForegroundColor Green
}

# 4. Activate virtual environment
Write-Host "Activating virtual environment..."
& ".\venv\Scripts\Activate.ps1"

# 5. Install dependencies
if (Test-Path "./requirements.txt") {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
} else {
    Write-Host "requirements.txt not found. Skipping." -ForegroundColor Red
}

# 6. Start backend in a new PowerShell window
Write-Host "Starting backend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command",
"cd `"$projectRoot`"; & `".\venv\Scripts\Activate.ps1`"; python -m uvicorn backend.api:app --reload"

# 7. Start frontend in a new PowerShell window
Write-Host "Starting frontend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command",
"cd `"$projectRoot`"; & `".\venv\Scripts\Activate.ps1`"; python -m streamlit run frontend/dashboard.py"

Write-Host ">>> Setup complete! Backend and frontend are running." -ForegroundColor Green

