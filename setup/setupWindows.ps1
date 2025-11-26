Write-Host "=== Automated Setup & Launch ==="

# Detect Python 3.11
function Test-Python311 {
    try {
        $ver = & python3.11 --version 2>$null
        return $ver -match "3\.11"
    } catch { return $false }
}

# Install Python 3.11 if missing
if (-not (Test-Python311)) {
    Write-Host "Python 3.11 not found. Installing via winget..."
    winget install -e --id Python.Python.3.11
}

# Virtual Environment
if (-not (Test-Path "./venv")) {
    Write-Host "Creating virtual environment..."
    python3.11 -m venv venv
}

Write-Host "Activating virtual environment..."
./venv/Scripts/Activate.ps1

Write-Host "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

Write-Host "Launching Backend..."
Start-Process powershell -ArgumentList "cd backend; ../venv/Scripts/python.exe -m uvicorn api:app --reload"

Write-Host "Launching Frontend..."
Start-Process powershell -ArgumentList "cd frontend; ../venv/Scripts/python.exe -m streamlit run dashboard.py"

Write-Host "Project is running!"
Write-Host "Backend → http://127.0.0.1:8000"
Write-Host "Frontend → http://localhost:8501"