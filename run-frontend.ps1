# run-frontend.ps1
# Set environment variables for the frontend
$env:API_BASE_URL="http://localhost:8000"
$env:REFRESH_MS="5000"

# Run the Streamlit dashboard
streamlit run frontend/dashboard.py