# backend/optimization/optimizer.py

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