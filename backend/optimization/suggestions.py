import pandas as pd
import torch
from torch import nn
import math

class StaffPredictor(nn.Module):
    def __init__(self):
        super(StaffPredictor, self).__init__()
        self.linear = nn.Linear(1,1)
    
    def forward(self,x):
        return self.linear(x)

def generate_optimization_plan():
    df = pd.read_csv("data/logisticsData.csv")
    staff_needed = df["inbound_volume"].values / 10
    X = df["inbound_volume"].values.reshape(-1,1)
    y = staff_needed.reshape(-1,1)

    X_tensor = torch.from_numpy(X).float()
    y_tensor = torch.from_numpy(y).float()

    model = StaffPredictor()
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

    for _ in range(200):
        optimizer.zero_grad()
        output = model(X_tensor)
        loss = criterion(output, y_tensor)
        loss.backward()
        optimizer.step()

    latest_volume = torch.tensor([[df["inbound_volume"].iloc[-1]]]).float()
    recommended_staff = model(latest_volume).item()
    return {"recommended_staff_hours": int(math.ceil(recommended_staff))}