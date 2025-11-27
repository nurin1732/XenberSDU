# backend/optimize.py

URGENT_MAP = {
    "sorting_capacity": "Sudden drop in sorting capacity — immediate intervention required.",
    "staff_available": "Anomaly in staff availability — deploy emergency team.",
    "vehicles_ready": "Vehicle readiness anomaly — dispatch disruption risk.",
    "congestion_level": "Abnormal congestion spike — clear buffers immediately.",
}

# Keep track of dismissed alerts so they don't re-appear after refresh
DISMISSED_ALERTS = set()


def optimize(latest, forecast, anomaly_vars=None):
    """
    Build comparison-based recommended actions based on the difference
    between latest metrics and 1-hour forecast.
    """
    if anomaly_vars is None:
        anomaly_vars = []

    actions = {}

    if not latest or not forecast:
        return actions

    # Sorting capacity dropping → risk of backlog
    if (
        "sorting_capacity" in latest
        and "sorting_capacity" in forecast
        and forecast["sorting_capacity"] < latest["sorting_capacity"] - 10
    ):
        actions["sorting_capacity"] = (
            "Sorting capacity expected to drop — increase throughput or reassign staff."
        )

    # Staff availability decreasing
    if (
        "staff_available" in latest
        and "staff_available" in forecast
        and forecast["staff_available"] < latest["staff_available"] - 5
    ):
        actions["staff_available"] = (
            "Staff availability may decrease — prepare backup workers."
        )

    # Vehicle readiness decreasing
    if (
        "vehicles_ready" in latest
        and "vehicles_ready" in forecast
        and forecast["vehicles_ready"] < latest["vehicles_ready"] - 3
    ):
        actions["vehicles_ready"] = (
            "Vehicle readiness dropping — adjust dispatch timing or activate standby units."
        )

    # Congestion increasing
    if (
        "congestion_level" in latest
        and "congestion_level" in forecast
        and forecast["congestion_level"] > latest["congestion_level"] + 0.1
    ):
        actions["congestion_level"] = (
            "Congestion expected to rise — reroute or boost sorting throughput."
        )

    return actions


def get_urgent_alerts(anomaly_vars):
    """
    Build a list of urgent alert objects from anomaly variables,
    excluding any that have been dismissed.
    """
    alerts = []
    for var in anomaly_vars:
        if var in URGENT_MAP and var not in DISMISSED_ALERTS:
            alerts.append(
                {
                    "id": var,             # simple stable ID per variable
                    "variable": var,
                    "message": URGENT_MAP[var],
                }
            )
    return alerts


def dismiss_alert(alert_id: str):
    """
    Mark an alert as dismissed so it won't appear again on refresh.
    """
    DISMISSED_ALERTS.add(alert_id)