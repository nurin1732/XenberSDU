URGENT_ALERTS = {}

def optimize(latest, forecast, anomaly_vars=None):
    """
    Generate recommended operational actions based on which variables
    are showing anomalies.
    """
    if anomaly_vars is None:
        anomaly_vars = []

    ACTIONS = {
        "sorting_capacity": "Increase sorting throughput by adjusting machine schedules or reallocating tasks.",
        "staff_available": "Bring in backup staff or redistribute team workload.",
        "vehicles_ready": "Activate additional vehicles or streamline dispatch timing.",
        "congestion_level": "Reroute parcels or expand sorting buffer capacity to reduce congestion.",
    }

    recommendations = {}

    # Only suggest actions for variables that are actually anomalous
    for var in anomaly_vars:
        if var in ACTIONS:
            recommendations[var] = ACTIONS[var]

    return recommendations

def compare_actions(latest, forecast):
    actions = {}

    if forecast["sorting_capacity"] < latest["sorting_capacity"] - 10:
        actions["sorting_capacity"] = (
            "Sorting capacity expected to drop — increase throughput or reassign staff."
        )

    if forecast["staff_available"] < latest["staff_available"] - 5:
        actions["staff_available"] = (
            "Staff availability may decrease — prepare backup workers."
        )

    if forecast["vehicles_ready"] < latest["vehicles_ready"] - 3:
        actions["vehicles_ready"] = (
            "Vehicle readiness dropping — adjust dispatch timing or activate standby units."
        )

    if forecast["congestion_level"] > latest["congestion_level"] + 0.1:
        actions["congestion_level"] = (
            "Congestion expected to rise — reroute or boost sorting throughput."
        )

    return actions

def add_urgent_alert(anomalies):
    global URGENT_ALERTS

    urgent_map = {
        "sorting_capacity": "Sudden drop in sorting capacity — immediate intervention required.",
        "staff_available": "Anomaly in staff availability — deploy emergency team.",
        "vehicles_ready": "Vehicle readiness anomaly — dispatch disruption risk.",
        "congestion_level": "Abnormal congestion spike — clear buffers immediately.",
    }

    for var in anomalies:
        if var in urgent_map:
            URGENT_ALERTS[var] = urgent_map[var]