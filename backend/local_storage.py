import pandas as pd
import os
import random
from datetime import datetime, timedelta
from backend.data_generate import generate_initial_history

CSV_PATH = "backend/data/history.csv"


# -----------------------------
# Initialize history
# -----------------------------
def init_history():
    """Ensure CSV exists with at least one initial row."""
    if not os.path.exists("backend/data"):
        os.makedirs("backend/data")

    # If no file OR file is empty → create a clean initial dataset
    if not os.path.exists(CSV_PATH) or os.path.getsize(CSV_PATH) == 0:
        df = generate_initial_history()
        print("🔄 Creating new history.csv with initial row")
        df.to_csv(CSV_PATH, index=False)


# -----------------------------
# Load Data
# -----------------------------
def load_data():
    """Load CSV safely with timestamp parsing."""
    if not os.path.exists(CSV_PATH):
        init_history()

    try:
        df = pd.read_csv(CSV_PATH, parse_dates=["timestamp"])
    except Exception:
        # Fallback: file corrupted → recreate
        print("⚠ history.csv corrupted — recreating file")
        init_history()
        df = pd.read_csv(CSV_PATH, parse_dates=["timestamp"])

    return df


# -----------------------------
# Append new synthetic row
# -----------------------------
def append_random_row():
    """Generate new 30-minute synthetic datapoint."""
    df = load_data()

    # Generate next timestamp
    if df.empty:
        timestamp = datetime.now().replace(second=0, microsecond=0)
    else:
        last_ts = pd.to_datetime(df["timestamp"].iloc[-1])
        timestamp = last_ts + timedelta(minutes=30)

    # Create synthetic metrics
    new_row = {
        "timestamp": timestamp,
        "sorting_capacity": random.randint(70, 120),
        "staff_available": random.randint(8, 25),
        "vehicles_ready": random.randint(5, 12),
        "congestion_level": round(random.uniform(0.1, 0.9), 3),
        "inbound_volume": random.randint(100, 250),
        "outbound_volume": random.randint(50, 200),
        "packages_arrived": random.randint(300, 600),
        "packages_departed": random.randint(150, 400),
    }

    # Append safely
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(CSV_PATH, index=False)

    return new_row