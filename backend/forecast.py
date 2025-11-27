import pandas as pd
import numpy as np
from datetime import timedelta
from sklearn.linear_model import LinearRegression


class Forecaster:
    """
    Timestamp-aware forecasting model using linear regression + 
    cyclic hour-of-day features (sin/cos) to introduce natural patterns.
    """

    def __init__(self):
        self.model = None
        self.columns = [
            "sorting_capacity",
            "staff_available",
            "vehicles_ready",
            "congestion_level"
        ]

    # ============================================================
    # CLEAN INPUT DATA
    # ============================================================
    def _clean_df(self, df):
        df = df.copy()
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.dropna(subset=self.columns)
        return df

    # ============================================================
    # CREATE CYCLIC TIME FEATURES
    # ============================================================
    def _add_time_features(self, df):
        df = df.copy()

        df["hour"] = df["timestamp"].dt.hour

        # Cyclic encoding
        df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
        df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)

        return df

    # ============================================================
    # FIT MODEL
    # ============================================================
    def fit(self, df):
        df = self._clean_df(df)
        df = self._add_time_features(df)

        if len(df) < 5:
            return None

        # features include KPIs + cyclic hour features
        feature_cols = self.columns + ["hour_sin", "hour_cos"]

        X = df[feature_cols].iloc[:-1]
        Y = df[self.columns].iloc[1:]

        model = LinearRegression()
        model.fit(X, Y)

        self.model = model
        return model

    # ============================================================
    # PREDICT NEXT STEP
    # ============================================================
    def _predict_next(self, last_row):
        # compute next timestamp
        next_ts = last_row["timestamp"] + timedelta(hours=1)
        next_hour = next_ts.hour

        hour_sin = np.sin(2 * np.pi * next_hour / 24)
        hour_cos = np.cos(2 * np.pi * next_hour / 24)

        # build feature vector
        features = pd.DataFrame([[
            last_row["sorting_capacity"],
            last_row["staff_available"],
            last_row["vehicles_ready"],
            last_row["congestion_level"],
            hour_sin,
            hour_cos
        ]], columns=self.columns + ["hour_sin", "hour_cos"])

        pred = self.model.predict(features)[0]

        return {
            "timestamp": next_ts,
            "sorting_capacity": int(max(pred[0], 0)),
            "staff_available": int(max(pred[1], 0)),
            "vehicles_ready": int(max(pred[2], 0)),
            "congestion_level": float(min(max(pred[3], 0), 1.0))
        }

    # ============================================================
    # 1-HOUR FORECAST
    # ============================================================
    def forecast_one_hour(self, df):
        if self.model is None:
            return None

        df = self._clean_df(df)
        last = df.iloc[-1].copy()

        return self._predict_next(last)

    # ============================================================
    # MULTI-STEP FORECAST (24H)
    # ============================================================
    def forecast_period(self, df, hours=24):
        if self.model is None:
            return None

        df = self._clean_df(df)
        last = df.iloc[-1].copy()

        rows = []

        for _ in range(hours):
            next_row = self._predict_next(last)
            rows.append(next_row)
            last = next_row  # recursive forecasting

        return pd.DataFrame(rows)