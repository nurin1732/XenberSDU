from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd

from backend.local_storage import init_history, load_data, append_random_row
from backend.anomaly import RollingZScoreAnomaly
from backend.forecast import Forecaster
from backend.optimize import optimize

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ---------------------------------------------------------
# Initialize CSV with history
# ---------------------------------------------------------
init_history()


# ---------------------------------------------------------
# Background scheduler (every 5 seconds)
# ---------------------------------------------------------
scheduler = BackgroundScheduler()

def auto_generate():
    print("Appending synthetic row...")
    append_random_row()

scheduler.add_job(auto_generate, "interval", seconds=5)
scheduler.start()


# ---------------------------------------------------------
# API ROUTES
# ---------------------------------------------------------
@app.get("/")
def home():
    return {"status": "OK", "message": "Backend running"}


@app.get("/data")
def data(limit: int = 300):
    df = load_data().sort_values("timestamp")
    df["timestamp"] = df["timestamp"].astype(str)
    return df.tail(limit).to_dict(orient="records")


@app.get("/forecast")
def forecast():
    df = load_data()
    if len(df) < 10:
        return {"error": "Need at least 10 rows"}

    fc = Forecaster()
    fc.fit(df)
    out = fc.forecast_period(hours=12)
    out["timestamp"] = out["timestamp"].astype(str)
    return out.to_dict(orient="records")


@app.get("/anomalies")
def anomalies(threshold: float = 2.5, window: int = 10):
    df = load_data()
    model = RollingZScoreAnomaly(window=window, threshold=threshold)
    out = model.compute(df)

    if out.empty:
        return {"anomalies": [], "status": "no_anomalies"}

    out["timestamp"] = out["timestamp"].astype(str)
    return {"anomalies": out.to_dict(orient="records"), "status": "anomalies_found"}


@app.get("/optimize")
def optimization():
    df = load_data()

    if df.empty:
        return {"error": "no data yet"}

    latest = df.iloc[-1].to_dict()

    # --- use the new one-hour forecast function ---
    fc = Forecaster()
    fc.fit(df)
    forecast_next = fc.forecast_one_hour()

    # If forecast unavailable
    if forecast_next is None:
        return {
            "status": "stable",
            "message": "Unable to generate forecast yet.",
            "latest": latest
        }

    # --- compute recommendations ---
    suggestions = optimize(latest, forecast_next)

    # If no real suggestions → system stable
    if not suggestions:
        return {
            "status": "stable",
            "message": "All metrics appear stable for the next hour.",
            "latest": latest,
            "forecast_next": forecast_next
        }

    return {
        "status": "action_required",
        "latest": latest,
        "forecast_next": forecast_next,
        "suggestions": suggestions
    }