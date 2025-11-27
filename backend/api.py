from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

import pandas as pd
import math
import uuid

from backend.local_storage import (
    load_data,
    init_history,
    append_random_row
)

from backend.anomaly import RollingZScoreAnomaly
from backend.forecast import Forecaster
from backend.optimize import optimize as build_suggestions, get_urgent_alerts, dismiss_alert



# ============================================================
# CLEAN JSON (remove NaN / inf)
# ============================================================
def clean_json(obj):
    if isinstance(obj, dict):
        return {k: clean_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_json(v) for v in obj]
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    return obj


# ============================================================
# FASTAPI APP
# ============================================================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


# ============================================================
# INIT DATA + BACKGROUND GENERATION
# ============================================================
init_history()

scheduler = BackgroundScheduler()


def auto_generate():
    print("Appending synthetic row...")
    append_random_row()


scheduler.add_job(auto_generate, "interval", seconds=5)
scheduler.start()


# ============================================================
# ROOT
# ============================================================
@app.get("/")
def root():
    return {"status": "running"}


# ============================================================
# GET HISTORY DATA
# ============================================================
@app.get("/data")
def data(limit: int = 500):
    df = load_data()

    if df.empty:
        return []

    df = df.sort_values("timestamp").tail(limit)
    df["timestamp"] = df["timestamp"].astype(str)

    return clean_json(df.to_dict(orient="records"))


# ============================================================
# ADD ONE RANDOM ROW
# ============================================================
@app.get("/append")
def append_row():
    row = append_random_row()
    row["timestamp"] = str(row["timestamp"])
    return clean_json(row)


# ============================================================
# ANOMALY DETECTION
# ============================================================
@app.get("/anomalies")
def anomalies(threshold: float = 2.5, window: int = 10):
    df = load_data()

    if df.empty:
        return {"anomalies": [], "status": "no_anomalies"}

    model = RollingZScoreAnomaly(window=window, threshold=threshold)
    out = model.compute(df)

    if out.empty:
        return {"anomalies": [], "status": "no_anomalies"}

    out["timestamp"] = out["timestamp"].astype(str)
    return clean_json({
        "anomalies": out.to_dict(orient="records"),
        "status": "found"
    })


# ============================================================
# 24-HOUR FORECAST
# ============================================================
@app.get("/forecast")
def forecast_24h():
    df = load_data()

    if df.empty or len(df) < 5:
        return {"error": "Not enough data for forecast"}

    fc = Forecaster()
    fc.fit(df)

    out = fc.forecast_period(df, hours=24)
    if out is None:
        return {"error": "Model not trained"}

    out["timestamp"] = out["timestamp"].astype(str)

    return clean_json(out.to_dict(orient="records"))


# ============================================================
# 1-HOUR FORECAST
# ============================================================
@app.get("/forecast_one_hour")
def forecast_one_hour():
    df = load_data()

    if df.empty or len(df) < 5:
        return {"error": "Not enough data"}

    fc = Forecaster()
    fc.fit(df)

    row = fc.forecast_one_hour(df)
    if row is None:
        return {"error": "Not enough data for 1-hour forecast"}

    row["timestamp"] = str(row["timestamp"])
    return clean_json(row)


# ============================================================
# OPTIMIZATION ENGINE
# ============================================================
@app.get("/optimize")
def optimization():
    df = load_data()

    if df.empty or len(df) < 5:
        return {"error": "Not enough data yet"}

    # ------------------------------------------
    # A) LATEST STATE
    # ------------------------------------------
    latest = df.iloc[-1].to_dict()

    # ------------------------------------------
    # B) FORECAST 1-HOUR
    # ------------------------------------------
    fc = Forecaster()
    fc.fit(df)
    one_hour = fc.forecast_one_hour(df)

    # ------------------------------------------
    # C) ANOMALY DETECTION
    # ------------------------------------------
    anomaly_model = RollingZScoreAnomaly(window=10, threshold=2.5)
    anomaly_df = anomaly_model.compute(df)

    anomaly_vars = []
    if anomaly_df is not None and len(anomaly_df) > 0:
        anomaly_vars = list(anomaly_df["variable"].unique())

    # ------------------------------------------
    # D) URGENT ALERTS (based on anomalies)
    # ------------------------------------------
    urgent_alerts = get_urgent_alerts(anomaly_vars)

    # ------------------------------------------
    # E) RECOMMENDED ACTIONS (comparison-based)
    # ------------------------------------------
    suggestions = build_suggestions(latest, one_hour, anomaly_vars)

    return clean_json({
        "latest": latest,
        "forecast_next": one_hour,
        "urgent_alerts": urgent_alerts,
        "suggestions": suggestions,
    })

# ============================================================
# DISMISS URGENT ALERT
# ============================================================
@app.post("/dismiss_alert")
def dismiss_alert_endpoint(alert_id: str):
    """
    Mark an urgent alert as dismissed so it doesn't reappear.
    """
    dismiss_alert(alert_id)
    return {"status": "ok", "dismissed": alert_id}