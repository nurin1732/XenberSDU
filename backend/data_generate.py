import pandas as pd
import random
from datetime import datetime, timedelta

COLUMNS = [
    "timestamp",
    "sorting_capacity",
    "staff_available",
    "vehicles_ready",
    "congestion_level"
]


def generate_initial_history(n=20):
    now = datetime.now().replace(second=0, microsecond=0)
    rows = []

    for i in range(n):
        ts = now - timedelta(minutes=30 * (n - i))
        rows.append([
            ts,
            random.randint(60, 100),
            random.randint(30, 60),
            random.randint(10, 20),
            random.uniform(0.1, 0.9)
        ])

    return pd.DataFrame(rows, columns=COLUMNS)


def generate_next_row(last_ts):
    next_ts = last_ts + timedelta(minutes=30)

    return {
        "timestamp": next_ts,
        "sorting_capacity": random.randint(60, 100),
        "staff_available": random.randint(30, 60),
        "vehicles_ready": random.randint(10, 20),
        "congestion_level": random.uniform(0.1, 0.9)
    }