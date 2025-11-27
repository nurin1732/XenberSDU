# backend/local_storage.py

import os
import pandas as pd
from datetime import datetime, timedelta

from backend.data_generate import (
    generate_initial_history,
    generate_next_row
)

CSV_PATH = "backend/data/history.csv"

COLUMNS = [
    "timestamp",
    "sorting_capacity",
    "staff_available",
    "vehicles_ready",
    "congestion_level"
]


# =============================================================
# INITIALISE CLEAN CSV (ALWAYS CONSISTENT)
# =============================================================
def init_history():
    """Ensure CSV exists with the correct schema and initial rows."""
    os.makedirs("backend/data", exist_ok=True)

    # If file missing or empty → regenerate clean dataset
    if not os.path.exists(CSV_PATH) or os.path.getsize(CSV_PATH) == 0:
        df = generate_initial_history(n=20)
        df.to_csv(CSV_PATH, index=False)
        print("🔄 Created fresh history.csv with realistic initial data")
        return

    # If CSV exists → load and ensure correct columns
    df = pd.read_csv(CSV_PATH)

    # If wrong schema → overwrite with clean dataset
    if list(df.columns) != COLUMNS:
        print("⚠ Wrong CSV schema detected — repairing...")
        df = generate_initial_history(n=20)
        df.to_csv(CSV_PATH, index=False)


# =============================================================
# LOAD CSV SAFELY
# =============================================================
def load_data():
    """Load CSV with timestamp parsing."""
    if not os.path.exists(CSV_PATH):
        init_history()

    df = pd.read_csv(CSV_PATH)

    # Parse timestamps correctly
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])  # remove any corrupted rows

    return df


# =============================================================
# APPEND NEW SYNTHETIC 30-MIN ROW
# =============================================================
def append_random_row():
    """Append next row based on the last timestamp."""
    df = load_data()

    # Determine next timestamp
    last_ts = df["timestamp"].iloc[-1] if not df.empty else \
              datetime.now().replace(second=0, microsecond=0)

    new_row = generate_next_row(last_ts)

    # Append
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(CSV_PATH, index=False)

    return new_row