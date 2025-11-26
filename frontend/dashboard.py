import os 
import time 
import json 
import requests 
import pandas as pd 
import numpy as np 
import streamlit as st 
from datetime import datetime 
from streamlit_autorefresh import st_autorefresh 
 
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
def safe_df(data): 
    if isinstance(data, list): 
        return pd.DataFrame(data) 
    if isinstance(data, dict): 
        return pd.DataFrame([data]) 
    return pd.DataFrame() 
@st.cache_data(show_spinner=False) 
 
def cached_api_get(path, params=None): 
    try: 
        resp = requests.get(f"{API_BASE_URL}{path}", params=params, timeout=5) 
        resp.raise_for_status() 
        return resp.json(), None 
    except Exception as e: 
        return None, str(e) 
 
def api_get(path, params=None, timeout=5): 
    url = f"{API_BASE_URL}{path}" 
    try: 
        resp = requests.get(url, params=params, timeout=timeout) 
        resp.raise_for_status() 
        return resp.json(), None 
    except Exception as e: 
        return None, str(e) 
 
def as_timeseries_df_safe(series_dict): 
    """ 
    Convert list of dicts (or empty/scalar data) to a DataFrame with 'timestamp' and 'value' columns. 
    Always returns a valid DataFrame even if input is empty or invalid. 
    """ 
    # Handle None, scalar, or empty input 
    if not series_dict or not isinstance(series_dict, list): 
        return pd.DataFrame(columns=["timestamp", "value"]) 
 
    # Convert list of dicts to DataFrame 
    try: 
        df = pd.DataFrame(series_dict) 
    except Exception: 
        return pd.DataFrame(columns=["timestamp", "value"]) 
 
    # Ensure timestamp column exists 
    if "timestamp" in df.columns: 
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce") 
    elif "ds" in df.columns: 
        df.rename(columns={"ds": "timestamp"}, inplace=True) 
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce") 
    else: 
        # fallback: if first column exists, use as timestamp 
        if df.shape[1] >= 1: 
            df.insert(0, "timestamp", pd.to_datetime(df.iloc[:, 0], errors="coerce")) 
        else: 
            df["timestamp"] = pd.NaT 
 
    # Ensure value column exists 
    if "value" not in df.columns: 
        if "yhat" in df.columns: 
            df.rename(columns={"yhat": "value"}, inplace=True) 
        elif df.shape[1] >= 2: 
            df.rename(columns={df.columns[1]: "value"}, inplace=True) 
        else: 
            df["value"] = np.nan 
 
    # Sort by timestamp if possible 
    if "timestamp" in df.columns: 
        df = df.sort_values("timestamp").reset_index(drop=True) 
    return df 
 
def card_metric(label, value, delta=None, help_text=None): 
    st.metric(label, value, delta=delta) 
    if help_text: 
        st.caption(help_text) 
 
# ----------------------------- 
# Sidebar 
# ----------------------------- 
with st.sidebar: 
    st.title("Controls") 
    st.text_input("API base URL", API_BASE_URL, key="api_base_url") 
    auto_refresh = st.checkbox("Use auto-refresh", value=True, key="auto_refresh") 
    REFRESH_MS = st.number_input("Refresh interval (ms)", 1000, 60000, REFRESH_MS, 1000, key="refresh_ms") 
    st.divider() 
    st.caption("Filters") 
    period = st.selectbox("Forecast period", ["24h", "48h", "7d"], index=1) 
    anomaly_threshold = st.slider("Anomaly severity threshold", 0.0, 1.0, 0.6, 0.05) 
 
API_BASE_URL = st.session_state.get("api_base_url", API_BASE_URL) 
REFRESH_MS = st.session_state.get("refresh_ms", REFRESH_MS) 
 
# ----------------------------- 
# Auto-refresh 
# ----------------------------- 
if auto_refresh: 
    st_autorefresh(interval=REFRESH_MS, key="refresh") 
    try:
        st.query_params.update({"ts": str(int(time.time() * 1000))}) 
    except Exception: 
        pass 
 
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
# Helper to fetch data safely 
# ----------------------------- 
def fetch_data(endpoint, params=None): 
    data, err = api_get(endpoint, params) 
    if err: 
        st.error(f"API error ({endpoint}): {err}") 
        return pd.DataFrame() if endpoint in ["/forecast", "/anomalies", "/optimize", "/alerts"] else [] 
    return data 
 
# ----------------------------- 
# Home Tab 
# ----------------------------- 
with tab_home: 
    fc_data = fetch_data("/forecast", {"period": period}) 
    an_data = fetch_data("/anomalies", {"threshold": anomaly_threshold}) 
    op_data = fetch_data("/optimize") 
    al_data = fetch_data("/alerts") 
 
    df_fc = as_timeseries_df_safe(fc_data) 
 
    forecast_col = "value" if "value" in df_fc.columns else df_fc.columns[1] if len(df_fc.columns) > 1 else None 
 
    if forecast_col and not df_fc.empty: 
        last_val = df_fc[forecast_col].iloc[-1] 
        prev_val = df_fc[forecast_col].iloc[-2] if len(df_fc) > 1 else np.nan 
        delta = None if (np.isnan(last_val) or np.isnan(prev_val)) else round(last_val - prev_val, 2) 
    else: 
        last_val = prev_val = delta = np.nan 
 
    col1, col2, col3, col4 = st.columns(4) 
    with col1: card_metric("Latest KPI", f"{round(last_val, 2)}", delta, "From Forecast") 
    with col2: card_metric("Anomalies (last 48h)", len(an_data) if an_data else 0) 
    with col3: card_metric("Recommendations", len(op_data) if op_data else 0) 
    with col4: card_metric("Active Alerts", len(al_data) if al_data else 0) 
 
    st.divider() 
    st.subheader("Overview chart") 
    if not df_fc.empty and forecast_col: 
        st.line_chart(df_fc.set_index("timestamp")[forecast_col], height=250, width="stretch") 
    else: 
        st.info("Forecast data not available yet.") 
 
    if st.button("Retry Fetch Home Data"): 
        st.experimental_rerun() 
 
# ----------------------------- 
# Forecast Tab 
# ----------------------------- 
with tab_forecast: 
    fc_data = fetch_data("/forecast", {"period": period}) 
    df = as_timeseries_df_safe(fc_data) 
 
    forecast_col = "value" if "value" in df.columns else df.columns[1] if len(df.columns) > 1 else None 
 
    if df.empty or not forecast_col: 
        st.info("Forecast data not available yet.") 
    else: 
        col_l, col_r = st.columns([3,2]) 
        with col_l: 
            st.line_chart(df.set_index("timestamp")[forecast_col], height=350, width="stretch") 
        with col_r: 
            st.write("Summary") 
            st.write({ 
                "min": float(df[forecast_col].min()), 
                "max": float(df[forecast_col].max()), 
                "mean": float(df[forecast_col].mean()), 
                "std": float(df[forecast_col].std()), 
            }) 
        st.divider() 
        st.download_button( 
            "Download forecast (CSV)", 
            df.to_csv(index=False).encode("utf-8"), 
            file_name=f"forecast_{period}.csv", 
        ) 
    if st.button("Retry Fetch Forecast"): 
        st.experimental_rerun() 
 
# ----------------------------- 
# Anomaly Detection Tab 
# ----------------------------- 
with tab_anomaly: 
    an_data = fetch_data("/anomalies", {"threshold": anomaly_threshold}) 
    df = as_timeseries_df_safe(an_data) 
 
    if df.empty: 
        st.info("No anomalies detected or API not ready.") 
    else: 
        st.scatter_chart(
            height=350, width="stretch" 
        ) 
        st.divider() 
        st.dataframe(df, width="stretch", height=350) 
    if st.button("Retry Fetch Anomalies"): 
        st.experimental_rerun() 
 
# ----------------------------- 
# Optimization Tab 
# ----------------------------- 
with tab_opt: 
    op_data = fetch_data("/optimize") 
    df = safe_df(op_data) 
 
    if df.empty: 
        st.info("No optimization data yet.") 
    else: 
        # Add default priority if missing 
        if "priority" not in df.columns: 
            df["priority"] = "Medium" 
 
        priority_selection = st.multiselect( 
            "Filter by priority", ["High","Medium","Low"], ["High","Medium","Low"] 
        ) 
        df_f = df[df["priority"].isin(priority_selection)] 
 
        st.dataframe(df_f, width="stretch", height=350) 
        st.divider() 
        st.download_button( 
            "Download recommendations (CSV)", 
            df_f.to_csv(index=False).encode("utf-8"), 
            "optimization_recommendations.csv", 
        ) 
 
    if st.button("Retry Fetch Optimization"): 
        st.experimental_rerun() 
# ----------------------------- 
# Alerts Tab 
# ----------------------------- 
with tab_alerts: 
    al_data = fetch_data("/alerts") 
    df = safe_df(al_data) 
 
    if df.empty: 
        st.info("No alerts or API not ready.") 
    else: 
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce") 
        level_order = {"Critical":0,"Warning":1,"Info":2} 
        df["sort"] = df["level"].map(level_order) 
        df = df.sort_values(["sort","created_at"]) 
        for _, row in df.iterrows(): 
            level = row["level"] 
            with st.container(): 
                st.markdown(f"**[{level}]** {row['title']}") 
                st.caption(f"ID: {row['id']} • {row['created_at']}") 
                st.write(row["detail"]) 
                st.progress(0.9 if level=="Critical" else 0.6 if level=="Warning" else 0.3, text=f"{level} level") 
        st.divider() 
        st.download_button( 
            "Export alerts (JSON)", 
            json.dumps(al_data, indent=2).encode("utf-8"), 
            "alerts.json", 
            "application/json", 
        ) 
    if st.button("Retry Fetch Alerts"): 
        st.experimental_rerun() 
 
# ----------------------------- 
# Footer 
# ----------------------------- 
st.caption("Powered by PyTorch backend. Streamlit frontend.")