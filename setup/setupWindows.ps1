# Requires PowerShell 5+ or PowerShell 7+
# ===============================================
# setupWindows.ps1
# ===============================================

# Allow running scripts for this session
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# Move to project root (quote the path to handle spaces)
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$projectRoot\.."

# ===============================================
# 1. Create virtual environment if it doesn't exist
# ===============================================
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
} else {
    Write-Host "Virtual environment already exists."
}

# ===============================================
# 2. Activate virtual environment
# ===============================================
Write-Host "Activating virtual environment..."
& ".\venv\Scripts\Activate.ps1"

# ===============================================
# 3. Install dependencies
# ===============================================
Write-Host "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# ===============================================
# 4. Launch backend in a new PowerShell window
# ===============================================
Write-Host "Starting backend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd `"$PWD\backend`"; .\venv\Scripts\python.exe -m uvicorn api:app --reload"

# ===============================================
# 5. Wait until backend is ready
# ===============================================
Write-Host "Waiting for backend to start..."
while (-not (Test-NetConnection -ComputerName localhost -Port 8000).TcpTestSucceeded) {
    Start-Sleep -Seconds 1
}

# ===============================================
# 6. Launch frontend in a new PowerShell window
# ===============================================
Write-Host "Starting frontend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd `"$PWD\frontend`"; ..\venv\Scripts\python.exe -m streamlit run `"`dashboard.py`"`"

Write-Host "All done! Backend and frontend are running
