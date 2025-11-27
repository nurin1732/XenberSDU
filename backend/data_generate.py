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


# -------------------------------------------
# Helper: Apply realistic daily patterns
# -------------------------------------------
def apply_daily_patterns(timestamp, base):
    hour = timestamp.hour

    sorting_capacity = base["sorting_capacity"]
    staff = base["staff_available"]
    vehicles = base["vehicles_ready"]
    congestion = base["congestion_level"]

    # ===== REALISTIC DAILY PATTERNS =====

    # Morning surge: 8–11am
    if 8 <= hour <= 11:
        sorting_capacity += random.randint(10, 25)
        staff += random.randint(2, 5)
        congestion -= 0.1
        congestion = max(0.05, congestion)

    # Lunch slowdown: 12–2pm
    elif 12 <= hour <= 14:
        sorting_capacity -= random.randint(5, 15)
        staff -= random.randint(3, 6)
        congestion += 0.1

    # Afternoon congestion: 3–6pm
    elif 15 <= hour <= 18:
        congestion += random.uniform(0.15, 0.3)
        vehicles -= random.randint(1, 3)

    # Evening recovery: 7–10pm
    elif 19 <= hour <= 22:
        sorting_capacity += random.randint(5, 15)
        congestion -= random.uniform(0.05, 0.1)

    # Night low activity: 11pm–6am
    else:
        sorting_capacity -= random.randint(5, 12)
        staff -= random.randint(2, 4)
        congestion -= 0.05

    # Safety bounds
    sorting_capacity = max(sorting_capacity, 10)
    staff = max(staff, 3)
    vehicles = max(vehicles, 2)
    congestion = min(max(congestion, 0), 1)

    return {
        "sorting_capacity": sorting_capacity,
        "staff_available": staff,
        "vehicles_ready": vehicles,
        "congestion_level": congestion
    }


# -------------------------------------------
# Generate initial history
# -------------------------------------------
def generate_initial_history(n=20):
    now = datetime.now().replace(second=0, microsecond=0)
    rows = []

    for i in range(n):
        ts = now - timedelta(minutes=30 * (n - i))

        # Base values
        base = {
            "sorting_capacity": random.randint(60, 100),
            "staff_available": random.randint(30, 60),
            "vehicles_ready": random.randint(10, 20),
            "congestion_level": random.uniform(0.1, 0.9)
        }

        # Apply time-of-day realism
        adjusted = apply_daily_patterns(ts, base)

        rows.append([
            ts,
            adjusted["sorting_capacity"],
            adjusted["staff_available"],
            adjusted["vehicles_ready"],
            adjusted["congestion_level"],
        ])

    return pd.DataFrame(rows, columns=COLUMNS)


# -------------------------------------------
# Generate next row (for live updates)
# -------------------------------------------
def generate_next_row(last_ts):
    ts = last_ts + timedelta(minutes=30)

    # Base randomness
    base = {
        "sorting_capacity": random.randint(60, 100),
        "staff_available": random.randint(30, 60),
        "vehicles_ready": random.randint(10, 20),
        "congestion_level": random.uniform(0.1, 0.9)
    }

    # Apply realistic daily behaviour
    adjusted = apply_daily_patterns(ts, base)

    return {
        "timestamp": ts,
        **adjusted
    }