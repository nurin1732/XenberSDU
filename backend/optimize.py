def optimize(latest, forecast_next):
    suggestions = {}

    # ---------- SAFETY CHECK ----------
    if not latest or not forecast_next:
        return {"note": "Not enough data for optimization yet."}

    # ----- 1: Sorting Capacity -----
    if "sorting_capacity" in latest and "sorting_capacity" in forecast_next:
        diff = forecast_next["sorting_capacity"] - latest["sorting_capacity"]
        if diff > 10:
            suggestions["Sorting Capacity"] = (
                f"Sorting throughput may need to increase by ~{int(diff)} units."
            )

    # ----- 2: Staff Availability -----
    if "staff_available" in latest and "staff_available" in forecast_next:
        if forecast_next["staff_available"] < latest["staff_available"] - 5:
            suggestions["Staff Allocation"] = (
                "Expected staff shortage — consider reallocating additional staff."
            )

    # ----- 3: Vehicles Ready -----
    if "vehicles_ready" in latest and "vehicles_ready" in forecast_next:
        if forecast_next["vehicles_ready"] < 5:
            suggestions["Fleet Dispatch"] = (
                "Low vehicle availability forecasted — prepare more outbound vehicles."
            )

    # ----- 4: Congestion Level -----
    if "congestion_level" in latest and "congestion_level" in forecast_next:
        if forecast_next["congestion_level"] > 60:
            suggestions["Congestion Control"] = (
                "High congestion expected — activate load balancing or rerouting."
            )

    # ---------- STABLE FALLBACK ----------
    if not suggestions:
        return {
            "status": "stable",
            "message": "📘 System operating normally. No optimization required."
        }

    return suggestions