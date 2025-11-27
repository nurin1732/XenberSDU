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

tabs = st.tabs(["📊 KPIs", "🔍 Anomalies", "⚠ Optimization", "📈 Forecast"])

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

        if "status" in resp and resp["status"] == "no_anomalies":
            st.success("✅ No anomalies detected.")
        else:
            anomalies = resp["anomalies"]
            if len(anomalies) == 0:
                st.success("✅ No anomalies detected.")
            else:
                st.error("🚨 Anomalies Detected!")
                st.dataframe(anomalies)

    except Exception as e:
        st.error(e)



# -----------------------------------------
# TAB 3 — Optimization
# -----------------------------------------
with tabs[2]:
    st.subheader("⚡ Optimization Suggestions")

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

# -----------------------------------------
# TAB 4 — Forecast (Next 24 Hours)
# -----------------------------------------
with tabs[3]:
    st.subheader(" 24-Hour Forecast")

    try:
        out = requests.get(f"{BASE}/forecast").json()
        df_fc = pd.DataFrame(out)

        if df_fc.empty or "timestamp" not in df_fc.columns:
            st.warning("Forecast unavailable — need more historical data.")
        else:
            # Convert timestamp safely
            df_fc["timestamp"] = pd.to_datetime(df_fc["timestamp"], errors="coerce")

            #Convert numeric columns
            numeric_cols = [
                "sorting_capacity",
                "staff_available",
                "vehicles_ready",
                "inbound_volume",
                "outbound_volume",
                "packages_arrived",
                "packages_departed"
            ]

            # Convert all numeric values to int
            for col in numeric_cols:
                if col in df_fc.columns:
                    df_fc[col] = df_fc[col].astype(int)

            # 🔥 Convert congestion_level to percentage (0–100)
            if "congestion_level" in df_fc.columns:
                df_fc["congestion_level"] = (df_fc["congestion_level"] * 100).astype(int)

            # Sort latest first for table
            df_fc = df_fc.sort_values("timestamp", ascending=False)

            # ==============================
            #     FORECAST LINE CHARTS
            # ==============================
            st.markdown("### 📊 Forecast Charts")

            # For charts, convert congestion % back to 0–1 scale
            df_chart = df_fc.copy()
            if "congestion_level" in df_chart.columns:
                df_chart["congestion_level"] = df_chart["congestion_level"] / 100.0

            for col in ["sorting_capacity", "staff_available", "vehicles_ready", "congestion_level"]:
                if col not in df_chart.columns:
                    continue

                fig = px.line(
                    df_chart.sort_values("timestamp"),
                    x="timestamp",
                    y=col,
                    markers=True
                )

                # Label congestion_level as %
                if col == "congestion_level":
                    fig.update_yaxes(tickformat=".0%")  # show % on chart

                fig.update_layout(height=280)
                st.plotly_chart(fig, width='stretch')

            # ==============================
            #     FORECAST TABLE
            # ==============================
            st.markdown("### 📋 Forecast Table (Latest First)")
            st.dataframe(df_fc)

    except Exception as e:
        st.error(f"Forecast error: {e}")