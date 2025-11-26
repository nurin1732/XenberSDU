# Requires PowerShell 5+ or PowerShell 7+
Write-Host "=== XenberSDU: Automated Setup & Launch (Windows PowerShell) ===`n"

# --- Detect Python 3.11 ---
$python = ""
if (Get-Command python3.11 -ErrorAction SilentlyContinue) {
    $python = "python3.11"
}
elseif (Get-Command py -ErrorAction SilentlyContinue) {
    # Check py launcher for 3.11
    $pyVersion = py -0p | Select-String "3.11"
    if ($pyVersion) { $python = "py -3.11" }
}

if ($python -eq "") {
    Write-Host "❌ Python 3.11 not found!"
    Write-Host "➡ Install it using one of these:"
    Write-Host "   • Windows Store:  Python 3.11"
    Write-Host "   • Official:       https://python.org/downloads/"
    Write-Host "   • Pyenv-win:      pyenv install 3.11.7"
    exit 1
}

Write-Host "Using Python: $python`n"

# --- Create Virtual Environment ---
if (!(Test-Path "venv")) {
    Write-Host "Creating virtual environment (Python 3.11)..."
    cmd.exe /c "$python -m venv venv"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create venv"
        exit 1
    }
}

Write-Host "Activating virtual environment..."
. .\venv\Scripts\Activate.ps1

if (-not $env:VIRTUAL_ENV) {
    Write-Host "❌ Could not activate venv"
    exit 1
}

# --- Install Dependencies ---
Write-Host "`nInstalling dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed installing requirements"
    exit 1
}

$ROOT = (Get-Location).Path

# --- Launch Backend in New PowerShell Window ---
Write-Host "`nLaunching Backend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd `"$ROOT`"; .\venv\Scripts\Activate.ps1; uvicorn backend.api:app --reload"

# --- Launch Frontend in New PowerShell Window ---
Write-Host "Launching Frontend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd `"$ROOT\frontend`"; ..\venv\Scripts\Activate.ps1; streamlit run dashboard.py"

Write-Host "`n🎉 Project running!"
Write-Host "Backend → http://127.0.0.1:8000"
Write-Host "Frontend → http://localhost:8501"