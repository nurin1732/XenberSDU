import pandas as pd
import torch
from torch import nn

class Autoencoder(nn.Module):
    def __init__(self, input_size=4, hidden_size=8):
        super(Autoencoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(hidden_size, input_size),
        )
    
    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

def detect_anomalies():
    df = pd.read_csv("data/logisticsData.csv")
    X = df[["inbound_volume","outbound_volume","truck_arrivals","trailer_temp"]].values.astype(float)
    X_tensor = torch.from_numpy(X).float()

    model = Autoencoder(input_size=4)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

    # Train autoencoder (short epochs for demo)
    for _ in range(200):
        optimizer.zero_grad()
        output = model(X_tensor)
        loss = criterion(output, X_tensor)
        loss.backward()
        optimizer.step()

    # Compute reconstruction error
    with torch.no_grad():
        recon = model(X_tensor)
        error = ((X_tensor - recon)**2).mean(dim=1)
    
    threshold = error.mean() + 2*error.std()
    df["anomaly"] = (error > threshold).int()
    df["severity"] = df["anomaly"]

    anomalies = df[df["anomaly"]==1]
    return anomalies.tail(20)[["timestamp","inbound_volume","truck_arrivals","severity"]].to_dict(orient="records")