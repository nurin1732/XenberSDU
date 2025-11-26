from fastapi import FastAPI
from backend.forecasting.forecast import get_forecast_pytorch
from backend.anomaly.anomalyDetection import detect_anomalies
from backend.optimization.suggestions import generate_optimization_plan
from backend.utils.dataGeneration import simulate_logistics_data
from datetime import datetime

app = FastAPI()

# Generate data on startup
simulate_logistics_data()

@app.get("/")
def home():
    return {"message": "Logistics AI Backend Running"}

@app.get("/forecast")
def forecast():
    result = get_forecast_pytorch()
    return result if isinstance(result, list) else [result]

@app.get("/anomalies")
def anomalies():
    result = detect_anomalies()
    return result if isinstance(result, list) else [result]

@app.get("/optimize")
def optimize():
    result = generate_optimization_plan()
    return result if isinstance(result, list) else [result]

@app.get("/alerts")
def alerts():
    anomalies = detect_anomalies()
    forecast = get_forecast_pytorch()

    alert = {
        "id": 1,
        "level": "Warning" if len(anomalies) else "Info",
        "title": "System Status Update",
        "detail": f"Detected {len(anomalies)} anomalies, peak inbound volume = "
                  f"{max([i['yhat'] for i in forecast])}",
        "created_at": datetime.utcnow().isoformat()
    }

    return [alert]  # ensure list response
