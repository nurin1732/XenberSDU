import pandas as pd
import numpy as np
import torch
from torch import nn

class LSTMForecast(nn.Module):
    def __init__(self, input_size=1, hidden_size=50, num_layers=1):
        super(LSTMForecast, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.linear = nn.Linear(hidden_size, 1)
    
    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.linear(out[:, -1, :])
        return out

def get_forecast_pytorch(seq_length=10, predict_hours=24, epochs=100, lr=0.01):
    df = pd.read_csv("data/logisticsData.csv")
    data = df["inbound_volume"].values.astype(float)
    
    # Normalize
    mean, std = data.mean(), data.std()
    data_norm = (data - mean) / std

    # Create sequences
    X, y = [], []
    for i in range(len(data_norm) - seq_length):
        X.append(data_norm[i:i+seq_length])
        y.append(data_norm[i+seq_length])

    X = np.array(X)
    y = np.array(y)

    X_tensor = torch.from_numpy(X).float().unsqueeze(-1)   # (N, seq_len, 1)
    y_tensor = torch.from_numpy(y).float().unsqueeze(-1)   # (N, 1)

    model = LSTMForecast()
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    # Train model
    for _ in range(epochs):
        optimizer.zero_grad()
        output = model(X_tensor)
        loss = criterion(output, y_tensor)
        loss.backward()
        optimizer.step()
    
    # Forecast loop
    last_seq = torch.from_numpy(data_norm[-seq_length:]).float().unsqueeze(0).unsqueeze(-1)
    # shape → (1, seq_len, 1)

    forecasts = []

    for _ in range(predict_hours):
        with torch.no_grad():
            pred = model(last_seq)   # shape: (1, 1)

        value = pred.item() * std + mean
        forecasts.append(value)

        # Fix: convert pred → (1, 1, 1)
        pred_expanded = pred.unsqueeze(0)  # → (1, 1, 1)

        # Update rolling window
        last_seq = torch.cat((last_seq[:, 1:, :], pred_expanded), dim=1)

    timestamps = pd.date_range(
        start=df['timestamp'].iloc[-1],
        periods=predict_hours + 1,
        freq='h'
    )[1:]

    return [
        {"ds": str(timestamps[i]), "yhat": float(forecasts[i])}
        for i in range(predict_hours)
    ]