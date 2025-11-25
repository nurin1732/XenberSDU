<#
.SYNOPSIS
    Setup script for Predictive Analytics SaaS
.DESCRIPTION
    Installs Python 3.11 (if missing), sets up virtual environment, installs dependencies from requirements.txt,
    and activates the virtual environment (Windows only). Provides instructions for macOS/Linux.
#>

Write-Host "=== Predictive Analytics SaaS Setup ==="

# Function to check if Python 3.11 exists
function Test-Python311 {
    try {
        $version = & python3.11 --version 2>$null
        if ($version -match "3\.11") { return $true } else { return $false }
    } catch {
        return $false
    }
}

# Detect OS
$OS = $PSVersionTable.OS
$IsWindowsOS = $false
if ($OS -match "Windows") { $IsWindowsOS = $true }
Write-Host "Detected OS: $OS"

# Install Python 3.11 if missing
if (-not (Test-Python311)) {
    Write-Host "Python 3.11 not found. Installing..."
    if ($IsWindows) {
        Write-Host "Installing Python 3.11 via winget..."
        winget install -e --id Python.Python.3.11
    } else {
        Write-Host "Installing Python 3.11 via Homebrew..."
        brew install python@3.11
        brew link --overwrite python@3.11
    }

    if (-not (Test-Python311)) {
        Write-Host "Python 3.11 installation failed. Please install manually." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Python 3.11 is already installed."
}

# Set paths
if ($IsWindows) {
    $PythonPath = "python3.11"
    $VenvActivate = ".\venv\Scripts\Activate.ps1"
} else {
    $PythonPath = "/usr/local/bin/python3.11"
    $VenvActivate = "./venv/bin/activate"
}

# Create virtual environment if not exists
if (-not (Test-Path "./venv")) {
    Write-Host "Creating virtual environment..."
    & $PythonPath -m venv ./venv
} else {
    Write-Host "Virtual environment already exists. Skipping creation."
}

# Install dependencies
& $PythonPath -m pip install --upgrade pip

if (Test-Path "./requirements.txt") {
    Write-Host "Installing Python packages from requirements.txt..."
    & $PythonPath -m pip install --upgrade --upgrade-strategy only-if-needed -r requirements.txt
} else {
    Write-Host "requirements.txt not found!"
}

# Activate virtual environment
if ($IsWindows) {
    Write-Host "Activating virtual environment..."
    if (Test-Path $VenvActivate) {
        Write-Host "Virtual environment activated for this PowerShell session."
        & $VenvActivate
    } else {
        Write-Host "Could not find Activate.ps1 script. Please activate manually: .\venv\Scripts\Activate.ps1"
    }
} else {
    Write-Host "`nTo activate the virtual environment on macOS/Linux, run:"
    Write-Host "    source $VenvActivate"
}

Write-Host "`nSetup complete! Virtual environment is ready."