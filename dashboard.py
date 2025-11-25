import os
import time
import json
import requests
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta

# -----------------------------
# Config
# -----------------------------
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
REFRESH_MS = int(os.getenv("REFRESH_MS", "5000"))

st.set_page_config(
    page_title="Enterprise Ops Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Utilities
# -----------------------------
def api_get(path, params=None, timeout=5):
    """
    Safe GET wrapper that falls back to mock data when API is unavailable.
    Returns (data, error). data is dict/list, error is None or str.
    """
    url = f"{API_BASE_URL}{path}"
    try:
        resp = requests.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
        return resp.json(), None
    except Exception as e:
        return None, str(e)

def as_timeseries_df(series_dict, date_key="timestamp", value_key="value"):
    """
    Convert API/Mock dict list to pandas DataFrame sorted by timestamp.
    Expects list of {timestamp: ISO8601, value: float}.
    """
    if isinstance(series_dict, list):
        df = pd.DataFrame(series_dict)
    else:
        df = pd.DataFrame(series_dict or [])
    if date_key in df.columns:
        df[date_key] = pd.to_datetime(df[date_key], errors="coerce")
        df = df.sort_values(date_key)
        df = df.reset_index(drop=True)
    return df

def card_metric(label, value, delta=None, help_text=None):
    """
    Render a simple metric card.
    """
    st.metric(label, value, delta=delta)
    if help_text:
        st.caption(help_text)

# -----------------------------
# Mock data generators (used until backend API is ready)
# -----------------------------
def mock_forecast(n_points=48, start=None):
    start = start or datetime.now() - timedelta(hours=n_points)
    base = 100
    timestamps = [start + timedelta(hours=i) for i in range(n_points)]
    values = base + np.linspace(-5, 15, n_points) + np.random.normal(0, 3, n_points)
    return [{"timestamp": t.isoformat(), "value": float(v)} for t, v in zip(timestamps, values)]

def mock_anomalies(n_points=48, anomaly_ratio=0.1):
    series = mock_forecast(n_points)
    df = pd.DataFrame(series)
    anomalies_idx = np.random.choice(range(n_points), max(1, int(n_points * anomaly_ratio)), replace=False)
    rows = []
    for i in anomalies_idx:
        rows.append({
            "timestamp": df.iloc[i]["timestamp"],
            "severity": float(np.random.uniform(0.5, 1.0)),
            "metric": "demand",
            "value": float(df.iloc[i]["value"]),
            "reason": "Deviation from expected pattern",
        })
    return rows

def mock_optimization(n_items=5):
    items = []
    for i in range(n_items):
        items.append({
            "id": f"OP-{100+i}",
            "category": np.random.choice(["Staffing", "Inventory", "Maintenance"]),
            "recommendation": np.random.choice([
                "Shift 2 adds 1 headcount",
                "Reorder SKU-12 by 150 units",
                "Advance maintenance of Line-B",
                "Delay purchase till next week",
            ]),
            "expected_impact": f"{np.random.randint(3,15)}% cost reduction",
            "priority": np.random.choice(["High", "Medium", "Low"]),
            "eta": (datetime.now() + timedelta(days=np.random.randint(1,7))).date().isoformat(),
        })
    return items

def mock_alerts(n=4):
    levels = ["Info", "Warning", "Critical"]
    alerts = []
    for i in range(n):
        alerts.append({
            "id": f"AL-{1000+i}",
            "level": np.random.choice(levels, p=[0.5, 0.35, 0.15]),
            "title": np.random.choice([
                "Unexpected demand spike",
                "Sensor dropouts detected",
                "Stockout risk in Warehouse A",
                "Processing queue backlog",
            ]),
            "detail": np.random.choice([
                "Investigate line throughput variance.",
                "Check network for device connectivity.",
                "Expedite purchase order for SKU-27.",
                "Scale workers on shift 1 temporarily.",
            ]),
            "created_at": datetime.now().isoformat(),
        })
    return alerts

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.title("Controls")
    st.text_input("API base URL", API_BASE_URL, key="api_base_url")
    st.checkbox("Use auto-refresh", value=True, key="auto_refresh")
    st.number_input("Refresh interval (ms)", min_value=1000, max_value=60000, value=REFRESH_MS, step=1000, key="refresh_ms")

    st.divider()
    st.caption("Demo filters")
    period = st.selectbox("Forecast period", ["24h", "48h", "7d"], index=1)
    anomaly_threshold = st.slider("Anomaly severity threshold", 0.0, 1.0, 0.6, 0.05)

# Update config live
API_BASE_URL = st.session_state.get("api_base_url", API_BASE_URL)
REFRESH_MS = int(st.session_state.get("refresh_ms", REFRESH_MS))

if st.session_state.get("auto_refresh", True):
    st.experimental_singleton.clear() if False else None  # placeholder, avoids warning; harmless
    st_autorefresh = st.experimental_rerun if False else None  # placeholder
    st.experimental_set_query_params(ts=str(int(time.time()*1000)))  # lightweight cache-bust
    st.experimental_data_editor if False else None  # noop
    st.experimental_show if False else None  # noop
    st.experimental_get_query_params()
    st_autorefresh_component = st.empty()
    st_autorefresh_component = st.autorefresh(interval=REFRESH_MS, key="refresh")

# -----------------------------
# Header
# -----------------------------
st.title("📊 Intelligent Predictive Analytics for Enterprise Operations")
st.caption("Forecast KPIs, detect anomalies, and recommend optimizations with actionable alerts.")

# -----------------------------
# Tabs
# -----------------------------
tab_home, tab_forecast, tab_anomaly, tab_opt, tab_alerts = st.tabs(
    ["Home", "Forecasting", "Anomaly Detection", "Optimization", "Alerts"]
)

# -----------------------------
# Home
# -----------------------------
with tab_home:
    col1, col2, col3, col4 = st.columns(4)
    # Pull a quick sample from APIs (with fallback)
    fc_data, fc_err = api_get("/forecast", params={"period": period})
    an_data, an_err = api_get("/anomalies", params={"threshold": anomaly_threshold})
    op_data, op_err = api_get("/optimize")
    al_data, al_err = api_get("/alerts")

    if fc_err: fc_data = mock_forecast(n_points=24 if period=="24h" else 48 if period=="48h" else 7*24)
    if an_err: an_data = mock_anomalies(n_points=48, anomaly_ratio=0.12)
    if op_err: op_data = mock_optimization(n_items=5)
    if al_err: al_data = mock_alerts(n=4)

    df_fc = as_timeseries_df(fc_data)
    last_val = df_fc["value"].iloc[-1] if not df_fc.empty else np.nan
    prev_val = df_fc["value"].iloc[-2] if len(df_fc) > 1 else np.nan
    delta = None if (np.isnan(last_val) or np.isnan(prev_val)) else round(last_val - prev_val, 2)

    with col1: card_metric("Latest KPI", f"{round(last_val, 2)}", delta, "From Forecast")
    with col2: card_metric("Anomalies (last 48h)", f"{len(an_data)}")
    with col3: card_metric("Recommendations", f"{len(op_data)}")
    with col4: card_metric("Active Alerts", f"{len(al_data)}")

    st.divider()
    st.subheader("Overview chart")
    if not df_fc.empty:
        st.line_chart(df_fc.set_index("timestamp")["value"], height=250, use_container_width=True)
    else:
        st.info("No forecast data available yet.")

# -----------------------------
# Forecasting
# -----------------------------
with tab_forecast:
    st.subheader("Forecasted KPI")
    fc_data, err = api_get("/forecast", params={"period": period})
    if err:
        st.warning("API unavailable, showing mock forecast.")
        fc_data = mock_forecast(n_points=24 if period=="24h" else 48 if period=="48h" else 7*24)

    df = as_timeseries_df(fc_data)
    if df.empty:
        st.info("No forecast data.")
    else:
        left, right = st.columns([3, 2])
        with left:
            st.line_chart(df.set_index("timestamp")["value"], height=350, use_container_width=True)
        with right:
            st.write("Summary")
            st.write({
                "min": float(df["value"].min()),
                "max": float(df["value"].max()),
                "mean": float(df["value"].mean()),
                "std": float(df["value"].std()),
            })
            st.caption("Trend and dispersion help estimate operational stability.")

        st.divider()
        st.download_button(
            label="Download forecast (CSV)",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=f"forecast_{period}.csv",
            mime="text/csv",
        )

# -----------------------------
# Anomaly Detection
# -----------------------------
with tab_anomaly:
    st.subheader("Detected anomalies")
    an_data, err = api_get("/anomalies", params={"threshold": anomaly_threshold})
    if err:
        st.warning("API unavailable, showing mock anomalies.")
        an_data = mock_anomalies(n_points=48, anomaly_ratio=0.12)

    df = pd.DataFrame(an_data)
    if df.empty:
        st.info("No anomalies detected.")
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.sort_values("timestamp")
        # Scatter plot with severity as color
        st.scatter_chart(
            df.rename(columns={"timestamp": "index"}).set_index("index")[["severity"]],
            height=350,
            use_container_width=True,
        )
        st.caption("Bubble intensity indicates severity. Use threshold to focus ops response.")
        st.divider()
        st.dataframe(
            df[["timestamp", "metric", "value", "severity", "reason"]],
            use_container_width=True,
            height=300,
        )

# -----------------------------
# Optimization
# -----------------------------
with tab_opt:
    st.subheader("Optimization recommendations")
    op_data, err = api_get("/optimize")
    if err:
        st.warning("API unavailable, showing mock recommendations.")
        op_data = mock_optimization(n_items=7)

    df = pd.DataFrame(op_data)
    if df.empty:
        st.info("No optimization output.")
    else:
        # Priority filter
        priority = st.multiselect("Filter by priority", ["High", "Medium", "Low"], default=["High", "Medium", "Low"])
        df_f = df[df["priority"].isin(priority)]
        st.dataframe(df_f, use_container_width=True, height=350)

        st.divider()
        st.download_button(
            label="Download recommendations (CSV)",
            data=df_f.to_csv(index=False).encode("utf-8"),
            file_name="optimization_recommendations.csv",
            mime="text/csv",
        )

# -----------------------------
# Alerts
# -----------------------------
with tab_alerts:
    st.subheader("Alerts panel")
    al_data, err = api_get("/alerts")
    if err:
        st.warning("API unavailable, showing mock alerts.")
        al_data = mock_alerts(n=6)

    # Sort by level then created_at
    level_order = {"Critical": 0, "Warning": 1, "Info": 2}
    al_df = pd.DataFrame(al_data)
    if al_df.empty:
        st.info("No active alerts.")
    else:
        al_df["sort_level"] = al_df["level"].map(level_order).fillna(9)
        al_df["created_at"] = pd.to_datetime(al_df["created_at"], errors="coerce")
        al_df = al_df.sort_values(["sort_level", "created_at"])

        for _, row in al_df.iterrows():
            level = row.get("level", "Info")
            color = "red" if level == "Critical" else "orange" if level == "Warning" else "blue"
            with st.container(border=True):
                st.markdown(f"**[{level}]** {row.get('title', '')}")
                st.caption(f"ID: {row.get('id','')} • {row.get('created_at','')}")
                st.write(row.get("detail", ""))
                st.progress(0.9 if level == "Critical" else 0.6 if level == "Warning" else 0.3, text=f"{level} level")

        st.divider()
        st.download_button(
            label="Export alerts (JSON)",
            data=json.dumps(al_data, indent=2).encode("utf-8"),
            file_name="alerts.json",
            mime="application/json",
        )

# -----------------------------
# Footer
# -----------------------------
st.caption("Powered by JamAI-based backend (RAG + multi-step), visualized in Streamlit. BM/EN supported in responses.")