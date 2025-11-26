#!/bin/bash
echo "=== XenberSDU: Automated Setup & Launch (macOS/Linux) ==="

# --- Detect Python 3.11 ---
if command -v python3.11 &> /dev/null; then
    PY=python3.11
elif command -v pyenv &> /dev/null && pyenv versions | grep -q "3.11"; then
    PY=$(pyenv which python3.11)
else
    echo "❌ Python 3.11 not found!"
    echo "➡ Install it using one of these:"
    echo "   • Homebrew: brew install python@3.11"
    echo "   • Pyenv:    pyenv install 3.11.7"
    exit 1
fi

echo "Using Python: $PY"

# --- Create Virtual Environment ---
if [ ! -d "venv" ]; then
    echo "Creating virtual environment (Python 3.11)..."
    $PY -m venv venv || { echo "❌ Failed to create venv"; exit 1; }
fi

echo "Activating venv..."
source venv/bin/activate || { echo "❌ Could not activate venv"; exit 1; }

# --- Install Dependencies ---
echo "Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt || { echo "❌ Failed installing requirements"; exit 1; }

ROOT=$(pwd)

# --- Launch Backend in New Terminal ---
echo "Launching Backend..."
osascript <<EOF
tell application "Terminal"
    do script "cd '$ROOT' && source venv/bin/activate && uvicorn backend.api:app --reload"
end tell
EOF

# --- Launch Frontend in New Terminal ---
echo "Launching Frontend..."
osascript <<EOF
tell application "Terminal"
    do script "cd '$ROOT'/frontend && source ../venv/bin/activate && streamlit run dashboard.py"
end tell
EOF

echo ""
echo "🎉 Project running!"
echo "Backend → http://127.0.0.1:8000"
echo "Frontend → http://localhost:8501"
