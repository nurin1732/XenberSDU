from fastapi import FastAPI
from backend.forecasting.forecast import get_forecast_pytorch
from backend.anomaly.anomalyDetection import detect_anomalies
from backend.optimization.suggestions import generate_optimization_plan
from backend.utils.dataGeneration import simulate_logistics_data
app = FastAPI()

# Generate data on startup
simulate_logistics_data()

@app.get("/")
def home():
    return {"message": "Logistics AI Backend Running"}

@app.get("/forecast")
def forecast():
    return get_forecast_pytorch()

@app.get("/anomalies")
def anomalies():
    return detect_anomalies()

@app.get("/optimize")
def optimize():
    return generate_optimization_plan()

@app.get("/alerts")
def alerts():
    anomalies = detect_anomalies()
    forecast = get_forecast_pytorch()
    return {
        "num_anomalies": len(anomalies),
        "peak_inbound_volume": max([i["yhat"] for i in forecast])
    }
