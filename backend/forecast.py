import pandas as pd
from sklearn.linear_model import LinearRegression


class Forecaster:
    def fit(self, df):
        df = df.copy()
        df["time_index"] = range(len(df))

        self.models = {}
        for col in ["sorting_capacity", "staff_available", "vehicles_ready", "congestion_level"]:
            X = df[["time_index"]]
            y = df[col]
            model = LinearRegression().fit(X, y)
            self.models[col] = model

        self.last_index = len(df)

    def forecast_period(self, hours=24):
        steps = (hours * 60) // 30  # 30-minute intervals
        future_idx = list(range(self.last_index, self.last_index + steps))

        forecast = {}
        for col, model in self.models.items():
            forecast[col] = model.predict(pd.DataFrame({"time_index": future_idx}))

        df = pd.DataFrame(forecast)
        df["timestamp"] = pd.date_range(
            periods=steps,
            freq="30min",
            start=df["timestamp"].iloc[-1] if "timestamp" in df else pd.Timestamp.now()
        )

        return df
    
    def forecast_one_hour(self):
        """Return a single-row 1-hour forecast matching the KPI schema."""
        future_df = self.forecast_period(hours=1)

        # Make sure there's at least 1 row
        if future_df.empty:
            return None

        return future_df.iloc[0].to_dict()