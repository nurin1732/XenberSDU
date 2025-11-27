import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import requests
import plotly.express as px

# AUTO REFRESH EVERY 5s
st_autorefresh(interval=5000, key="auto_refresh")

st.set_page_config(page_title="Operations Dashboard", layout="wide")

BASE = "http://127.0.0.1:8000"

st.title("📦 Operations Control Dashboard")

tabs = st.tabs([" KPIs", "🔍Anomalies", "Forecast", "Optimization"])

# -----------------------------------------
# TAB 1 — LIVE KPIs
# -----------------------------------------
with tabs[0]:
    st.subheader("Live Operational Metrics")

    # === Interval selection ===
    interval = st.selectbox(
        "Select KPI Display Interval:",
        ["Last 1 hour", "Last 3 hours", "Last 6 hours", "Last 12 hours", "Last 24 hours", "All Data"],
        index=3
    )

    # Map choice → hours
    interval_hours = {
        "Last 1 hour": 1,
        "Last 3 hours": 3,
        "Last 6 hours": 6,
        "Last 12 hours": 12,
        "Last 24 hours": 24,
        "All Data": None
    }

    try:
        # Load data
        data = requests.get(f"{BASE}/data").json()
        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"], format="mixed")

        # Apply interval filter
        if interval_hours[interval] is not None:
            cutoff = df["timestamp"].max() - pd.Timedelta(hours=interval_hours[interval])
            df = df[df["timestamp"] >= cutoff]

        # Load anomalies
        anomalies = requests.get(f"{BASE}/anomalies").json()
        df_anom = pd.DataFrame(anomalies)
        if not df_anom.empty:
            df_anom["timestamp"] = pd.to_datetime(df_anom["timestamp"])

        # === KPI charts with anomaly markers ===
        for col in ["sorting_capacity", "staff_available", "vehicles_ready", "congestion_level"]:
            fig = px.line(df, x="timestamp", y=col, markers=True)

            # === FIXED ANOMALY HIGHLIGHTING ===
            if not df_anom.empty:
                df_anom_col = df_anom[df_anom["variable"] == col]

                if not df_anom_col.empty:
                    fig.add_scatter(
                        x=df_anom_col["timestamp"],
                        y=df_anom_col[col],
                        mode="markers",
                        marker=dict(size=10, color="red", symbol="circle"),
                        name="Anomaly"
                    )

            st.plotly_chart(fig, width='stretch')

    except Exception as e:
        st.error(e)


# ------------------------------------------------
# TAB 2 — ANOMALIES (with slider + indicator)
# ------------------------------------------------
with tabs[1]:
    st.subheader("🔍 Anomaly Detection")

    st.caption("Adjust detection sensitivity (lower threshold → more anomalies)")
    
    # Sensitivity controls
    threshold = st.slider(
        "Z-Score Threshold",
        min_value=0.5,
        max_value=5.0,
        value=2.5,
        step=0.1,
    )

    window = st.slider(
        "Rolling Window Size",
        min_value=3,
        max_value=30,
        value=10,
        step=1,
    )

    try:
        resp = requests.get(
            f"{BASE}/anomalies?threshold={threshold}&window={window}"
        ).json()

        if resp.get("status") == "no_anomalies":
            st.success("✅ No anomalies detected.")
        else:
            anomalies = resp.get("anomalies", [])

            if len(anomalies) == 0:
                st.success("✅ No anomalies detected.")
            else:
                df_anom = pd.DataFrame(anomalies)

                # Convert timestamp for sorting
                if "timestamp" in df_anom.columns:
                    df_anom["timestamp"] = pd.to_datetime(df_anom["timestamp"], format="mixed")
                    df_anom = df_anom.sort_values("timestamp", ascending=False)

                st.error("🚨 Anomalies Detected!")
                st.markdown("### 📋 Latest Anomalies (Newest First)")
                st.dataframe(df_anom)

    except Exception as e:
        st.error(f"Anomaly Error: {e}")
# ------------------------------------------------
# TAB 3 — FORECAST (24 HOURS ONLY)
# ------------------------------------------------
with tabs[2]:
    st.subheader("📈 24-Hour Forecast")

    try:
        fc24 = requests.get(f"{BASE}/forecast").json()

        # Handle backend errors
        if isinstance(fc24, dict) and "error" in fc24:
            st.warning(fc24["error"])
        else:
            df_fc24 = pd.DataFrame(fc24)

            if df_fc24.empty or "timestamp" not in df_fc24.columns:
                st.warning("Not enough information for 24-hour forecast.")
            else:
                # Convert timestamp
                df_fc24["timestamp"] = pd.to_datetime(df_fc24["timestamp"], format="mixed")

                # Convert congestion to percentage
                df_fc24["congestion_level"] = (df_fc24["congestion_level"] * 100).round(1)

                # Ensure integer formatting for integer KPIs
                for col in ["sorting_capacity", "staff_available", "vehicles_ready"]:
                    df_fc24[col] = df_fc24[col].astype(int)

                # ---------------------------------------------------------
                # GRAPHS
                # ---------------------------------------------------------
                st.markdown("### 📉 Forecast Trends (24 Hours)")

                for col in ["sorting_capacity", "staff_available", "vehicles_ready", "congestion_level"]:
                    fig = px.line(df_fc24, x="timestamp", y=col, markers=True)
                    fig.update_layout(height=260)
                    st.plotly_chart(fig, width='stretch')

                # ---------------------------------------------------------
                # TABLE
                # ---------------------------------------------------------
                st.markdown("### 📋 Forecast Table (24 Hours)")
                st.dataframe(df_fc24.sort_values("timestamp", ascending=False))

    except Exception as e:
        st.error(f"24-Hour Forecast Error: {e}")

# -----------------------------------------
# TAB 4 — Optimization
# -----------------------------------------
with tabs[3]:

    out = requests.get(f"{BASE}/optimize").json()

    # ---- LATEST METRICS (not dropdown, not JSON) ----
    if "latest" in out:
        latest = out["latest"]
        st.markdown("### 📌 Latest Metrics (Current Status)")

        cols = st.columns(4)
        metric_keys = list(latest.keys())

        # Display in 4-column grid, excluding timestamp
        display_keys = [k for k in metric_keys if k != "timestamp"]

        for i, key in enumerate(display_keys):

            value = latest[key]

            if key == "congestion_level":
                value = f"{value*100:.1f}%"

            cols[i % 4].metric(label=key.replace("_", " ").title(), value=value)
        st.markdown("---")

    # ---- 1-HOUR FORECAST (metric-style, same layout) ----
    if "forecast_next" in out:
        fc = out["forecast_next"]
        st.markdown("### 🕒 1-Hour Forecast")

        # Convert values
        formatted_fc = {}
        for key, value in fc.items():
            if key == "timestamp":
                formatted_fc[key] = value
            elif key == "congestion_level":
                formatted_fc[key] = f"{int(value * 100)}%"
            else:
                formatted_fc[key] = int(value)

        # Display in metric grid
        cols_fc = st.columns(4)
        for i, (key, value) in enumerate(formatted_fc.items()):
            if key == "timestamp":
                continue

            label = key.replace("_", " ").title()
            cols_fc[i % 4].metric(label=label, value=value)

        st.caption(f"Forecast time: {formatted_fc['timestamp']}")
        st.markdown("---")

    # ---- RECOMMENDATIONS ----
    st.markdown("### 💡 Recommended Actions")

    suggestions = out.get("suggestions", {})

    if suggestions.get("status") == "stable":
        st.success(" System operating normally. No optimization required.")
    else:
        actions = suggestions.get("actions", [])
        if not actions:
            st.info("No optimization suggestions available at the moment.")
        else:
            for act in actions:
                st.write(f"• {act}")