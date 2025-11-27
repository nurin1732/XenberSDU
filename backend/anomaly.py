import pandas as pd


class RollingZScoreAnomaly:
    def __init__(self, window=10, threshold=2.5):
        self.window = window
        self.threshold = threshold

    def compute(self, df):
        out = []

        for col in ["sorting_capacity", "staff_available", "vehicles_ready", "congestion_level"]:
            series = df[col]
            roll_mean = series.rolling(self.window).mean()
            roll_std = series.rolling(self.window).std()

            zscores = (series - roll_mean) / roll_std

            # Find anomalies
            anomalies = df[abs(zscores) > self.threshold]

            # 🔥 FIX: avoid SettingWithCopyWarning
            if not anomalies.empty:
                anomalies = anomalies.copy()                  # ← make safe copy
                anomalies.loc[:, "variable"] = col            # ← safe assignment
                out.append(anomalies)

        if not out:
            return pd.DataFrame()

        return pd.concat(out).sort_values("timestamp")