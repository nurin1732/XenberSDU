# backend/local_storage.py

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Where your CSV lives
DATA_FILE = "backend/data/history.csv"

# Global internal simulation clock
SIM_TIME = None


# ============================================================
# INITIALIZE HISTORY FILE
# ============================================================
def init_history():
    """
    Initialize the CSV if missing.
    Load the last timestamp if it exists.
    """
    global SIM_TIME

    os.makedirs("backend/data", exist_ok=True)

    # If file does not exist → create empty structure
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=[
            "timestamp",
            "sorting_capacity",
            "staff_available",
            "vehicles_ready",
            "congestion_level",
        ])
        df.to_csv(DATA_FILE, index=False)
        SIM_TIME = datetime.now().replace(second=0, microsecond=0)
        print("[INIT] Created new CSV history.")
        return

    # If CSV exists → load last timestamp
    df = pd.read_csv(DATA_FILE)

    if len(df) > 0:
        # Use last recorded timestamp
        SIM_TIME = pd.to_datetime(df["timestamp"].iloc[-1])
    else:
        SIM_TIME = datetime.now().replace(second=0, microsecond=0)

    print(f"[INIT] Loaded history. Last timestamp = {SIM_TIME}")


# ============================================================
# LOAD DATA
# ============================================================
def load_data():
    """Load existing CSV safely."""
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=[
            "timestamp",
            "sorting_capacity",
            "staff_available",
            "vehicles_ready",
            "congestion_level",
        ])

    df = pd.read_csv(DATA_FILE)

    # Convert timestamps
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.dropna(subset=["timestamp"])

    return df


# ============================================================
# REALISTIC GENERATION LOGIC
# ============================================================

def generate_sorting_capacity(hour):
    """
    Sorting capacity peaks during daytime.
    Smooth sinusoidal trend + noise.
    """
    cycle = np.sin(2 * np.pi * (hour - 6) / 24)
    cycle = (cycle + 1) / 2  # normalize 0–1
    base = 60 + 40 * cycle    # 60–100
    return max(0, int(base + np.random.normal(0, 3)))


def generate_staff_available(hour):
    """
    Shift-based staffing:
    8–16 => high, 16–24 => medium, night => low.
    """
    if 8 <= hour < 16:
        staff = 20 + np.random.normal(0, 2)
    elif 16 <= hour < 24:
        staff = 14 + np.random.normal(0, 2)
    else:
        staff = 6 + np.random.normal(0, 1)

    return max(0, int(staff))


def generate_vehicles_ready(hour):
    """
    Vehicles peak before dispatch:
    - 8 AM
    - 4 PM
    """
    morning_peak = np.exp(-((hour - 8) ** 2) / 6)
    evening_peak = np.exp(-((hour - 16) ** 2) / 6)
    readiness = 4 + (morning_peak + evening_peak) * 6 + np.random.normal(0, 0.5)
    return max(0, int(readiness))


def generate_congestion(capacity, staff, vehicles, hour):
    """
    Congestion depends on (capacity, staff, time of day).
    Peaks midday (1 PM).
    """
    midday_pressure = np.exp(-((hour - 13) ** 2) / 20)

    congestion = (
        0.4 * (1 - capacity / 120) +
        0.3 * (1 - staff / 25) +
        0.2 * midday_pressure +
        0.1 * np.random.rand()
    )

    return float(min(max(congestion, 0.0), 1.0))


# ============================================================
# BUILD A SINGLE NEW ROW
# ============================================================
def generate_synthetic_row():
    global SIM_TIME
    hour = SIM_TIME.hour

    cap = generate_sorting_capacity(hour)
    staff = generate_staff_available(hour)
    veh = generate_vehicles_ready(hour)
    cong = generate_congestion(cap, staff, veh, hour)

    return {
        "timestamp": SIM_TIME.strftime("%Y-%m-%d %H:%M:%S"),
        "sorting_capacity": cap,
        "staff_available": staff,
        "vehicles_ready": veh,
        "congestion_level": cong,
    }


# ============================================================
# APPEND NEW ROW TO CSV
# (Called every 5 seconds → advances 30 minutes)
# ============================================================
def append_random_row():
    global SIM_TIME

    df = load_data()
    row = generate_synthetic_row()

    new_row_df = pd.DataFrame([row])
    df = pd.concat([df, new_row_df], ignore_index=True)

    df.to_csv(DATA_FILE, index=False)

    # Advance simulation time by 30 minutes
    SIM_TIME = SIM_TIME + timedelta(minutes=30)
    SIM_TIME = SIM_TIME.replace(second=0, microsecond=0)

    return row