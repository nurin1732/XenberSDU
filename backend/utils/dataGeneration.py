import pandas as pd
import numpy as np

def simulate_logistics_data(n=500):
    timestamps = pd.date_range(end=pd.Timestamp.now(), periods=n, freq="1h")

    df = pd.DataFrame({
        "timestamp": timestamps,
        "inbound_volume": np.random.poisson(lam=50, size=n),  # incoming shipments
        "outbound_volume": np.random.poisson(lam=45, size=n),  # outgoing shipments
        "truck_arrivals": np.random.randint(5, 15, size=n),   # trucks per hour
        "trailer_temp": 5 + np.random.randn(n)  # sensor for refrigerated trailers
    })

    df.to_csv("data/logisticsData.csv", index=False)
    return df

if __name__ == "__main__":
    simulate_logistics_data()