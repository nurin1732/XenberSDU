import pandas as pd
import os
import random
from datetime import datetime, timedelta

CSV_PATH = "backend/data/history.csv"

# All columns that will always exist
COLUMNS = [
    "timestamp",
    "sorting_capacity",
    "staff_available",
    "vehicles_ready",
    "congestion_level",      # 0–1 float
    "inbound_volume",
    "outbound_volume",
    "packages_arrived",
    "packages_departed"
]


# -----------------------------
# SAFE VALUE CLEANER
# -----------------------------
def safe_value(x):
    """Ensure no NaN / inf / invalid numeric value ever enters CSV."""
    if x is None:
        return 0
    if isinstance(x, float):
        if pd.isna(x) or x == float("inf") or x == float("-inf"):
            return 0
    return x


# -----------------------------
# INITIAL HISTORY GENERATOR
# -----------------------------
def generate_initial_history(n=20):
    now = datetime.now().replace(second=0, microsecond=0)
    rows = []

    for i in range(n):
        ts = now - timedelta(minutes=30 * (n - i))

        row = {
            "timestamp": ts,
            "sorting_capacity": safe_value(random.randint(60, 110)),
            "staff_available": safe_value(random.randint(10, 25)),
            "vehicles_ready": safe_value(random.randint(4, 12)),
            "congestion_level": safe_value(round(random.uniform(0.2, 0.8), 2)),
            "inbound_volume": safe_value(random.randint(150, 350)),
            "outbound_volume": safe_value(random.randint(80, 250)),
            "packages_arrived": safe_value(random.randint(300, 700)),
            "packages_departed": safe_value(random.randint(150, 500)),
        }

        rows.append(row)

    return pd.DataFrame(rows, columns=COLUMNS)


# -----------------------------
# ENSURE CSV EXISTS
# -----------------------------
def init_history():
    if not os.path.exists("backend/data"):
        os.makedirs("backend/data")

    if not os.path.exists(CSV_PATH) or os.path.getsize(CSV_PATH) == 0:
        df = generate_initial_history()
        df.to_csv(CSV_PATH, index=False)


# -----------------------------
# LOAD DATA
# -----------------------------
def load_data():
    if not os.path.exists(CSV_PATH):
        init_history()

    df = pd.read_csv(CSV_PATH, parse_dates=["timestamp"])

    # Additional safety: replace any corrupt numbers
    df = df.replace([float("inf"), float("-inf")], 0)
    df = df.fillna(0)

    return df


# -----------------------------
# APPEND NEW 30-MINUTE ROW
# -----------------------------
def append_random_row():
    df = load_data()

    if df.empty:
        last_ts = datetime.now().replace(second=0, microsecond=0)
    else:
        last_ts = df["timestamp"].iloc[-1]

    next_ts = last_ts + timedelta(minutes=30)

    new_row = {
        "timestamp": next_ts,
        "sorting_capacity": safe_value(random.randint(60, 110)),
        "staff_available": safe_value(random.randint(10, 25)),
        "vehicles_ready": safe_value(random.randint(4, 12)),
        "congestion_level": safe_value(round(random.uniform(0.2, 0.9), 2)),
        "inbound_volume": safe_value(random.randint(150, 350)),
        "outbound_volume": safe_value(random.randint(80, 250)),
        "packages_arrived": safe_value(random.randint(300, 700)),
        "packages_departed": safe_value(random.randint(150, 500)),
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(CSV_PATH, index=False)

    return new_row