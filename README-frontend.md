# Frontend (Streamlit) — Intelligent Predictive Analytics

## What this provides
- Multi-tab dashboard: Home, Forecasting, Anomaly Detection, Optimization, Alerts.
- Auto-refresh with configurable interval.
- Works with backend API, and gracefully falls back to mock data.
- Download buttons for CSV/JSON exports.
- Clean, judge-friendly layout.

## Prerequisites
- Python 3.9+ recommended
- Requirements installed at repo root

## Run
```bash
# From repo root, after installing requirements
export API_BASE_URL="http://localhost:8000"  # adjust if deployed
export REFRESH_MS=5000
streamlit run frontend/dashboard.py