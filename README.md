# XenberSIntelligent Predictive Analytics for Enterprise Operations
Hackathon CodeFest 2025 Xenber Track 1 Entry by the Sekai Dev Unit

## Prerequisites
Python 3.9 to 3.11 supported


## How to run
Windows
1. Open PowerShell
2. Go to project folder
   "cd <path-to-folder>\XenberSDU"
   (replace the <path-to-folder>with location of folder)
   (eg.cd C:\Users\Judge\Desktop\XenberSDU)
3. Bypass execution policy
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
4. Activate the virtual environment
   & ".\venv\Scripts\Activate.ps1"
5. Start the backend:
   & ".\venv\Scripts\python.exe" -m uvicorn backend.api:app --reload
   Keep this window open
6. Once the backend running, open a new Powershell window for frontend:
   cd "C:\Users\YourUsername\Downloads\XenberSDU" 
   & ".\venv\Scripts\python.exe" -m streamlit run frontend/dashboard.py

MacOS
1. Open Terminal
2. Go to project folder
   "cd <path-to-folder>/XenberSDU"
   (replace the <path-to-folder>with location of folder)
   (eg. cd /path/to/anywhere/XenberSDU)
1. Run:
   "chmod +x setup/setupMac.sh
    ./setup/setupMac.sh        "
