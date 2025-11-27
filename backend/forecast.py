import pandas as pd
import numpy as np
from datetime import timedelta
from sklearn.linear_model import LinearRegression


class Forecaster:
    """
    A simple multi-output forecasting model using LinearRegression.
    Predicts next-step values for all KPIs.
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
    # CLEAN INPUT DATA — remove NaN / inf safely
    # ============================================================
    def _clean_df(self, df):
        df = df.copy()

        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.dropna(subset=self.columns)  # remove bad rows

        return df

    # ============================================================
    # FIT MODEL
    # ============================================================
    def fit(self, df):
        df = self._clean_df(df)

        if len(df) < 5:
            return None  # not enough data

        # X(t) = current values
        X = df[self.columns].iloc[:-1]

        # Y(t+1) = next-step prediction target
        Y = df[self.columns].iloc[1:]

        model = LinearRegression()
        model.fit(X, Y)

        self.model = model
        return model

    # ============================================================
    # PREDICT NEXT 1 STEP
    # ============================================================
    def _predict_next(self, last_row):
        """
        Predict next values using the fitted model.
        last_row = dict-like containing the latest values.
        """

        # Build a DataFrame with *correct feature names*
        features = pd.DataFrame([[
            last_row["sorting_capacity"],
            last_row["staff_available"],
            last_row["vehicles_ready"],
            last_row["congestion_level"]
        ]], columns=self.columns)

        # Predict next step
        pred = self.model.predict(features)[0]

        # Convert to clean numeric types
        return {
            "sorting_capacity": int(max(pred[0], 0)),
            "staff_available": int(max(pred[1], 0)),
            "vehicles_ready": int(max(pred[2], 0)),
            "congestion_level": float(min(max(pred[3], 0.0), 1.0)),  # clamp 0–1
        }

    # ============================================================
    # 1-HOUR FORECAST
    # ============================================================
    def forecast_one_hour(self, df):
        df = self._clean_df(df)

        if df.empty or self.model is None:
            return None

        last = df.iloc[-1].copy()
        next_vals = self._predict_next(last)

        return {
            "timestamp": last["timestamp"] + timedelta(hours=1),
            **next_vals
        }

    # ============================================================
    # MULTI-STEP FORECAST (e.g., 24 hours)
    # ============================================================
    def forecast_period(self, df, hours=24):
        df = self._clean_df(df)

        if df.empty or self.model is None:
            return None

        last = df.iloc[-1].copy()
        rows = []

        # Predict repeatedly for the required number of hours
        for h in range(1, hours + 1):
            next_vals = self._predict_next(last)

            ts = last["timestamp"] + timedelta(hours=1)

            row = {
                "timestamp": ts,
                **next_vals
            }

            rows.append(row)

            # use this prediction as next input
            last = row

        return pd.DataFrame(rows)