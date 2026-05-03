from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
import torch
import torch.nn as nn

class SolarLSTM(nn.Module):
    def __init__(self, input_size):
        super().__init__()
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=64,
            num_layers=2,
            batch_first=True,
            dropout=0.2
        )
        
        self.fc = nn.Sequential(
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )

    def forward(self, x):
        out, _ = self.lstm(x)
        out = out[:, -1, :]
        return self.fc(out)


if __name__ == "__main__":
    df_pvgis = pd.read_csv('duzce_2020_pvgis_hourly_data.csv')
    df_open = pd.read_csv('duzce_2020_open_hourly_data.csv')

    df = pd.merge(df_pvgis.sort_values('time'), 
                df_open.sort_values('time'), 
                on='time')

    features = [
        "direct_normal_irradiance",
        "shortwave_radiation",
        "temperature_2m",
        "cloud_cover"
    ]

    scaler = MinMaxScaler()

    df[features + ["power_watt"]] = scaler.fit_transform(
        df[features + ["power_watt"]]
    )

    seq_len = 24

    inputs, outputs = [], []

    data = df[features + ["power_watt"]].values

    for i in range(len(data) - seq_len):
        inputs.append(data[i:i+seq_len, :-1])
        outputs.append(data[i+seq_len, -1])

    inputs = np.array(inputs)
    outputs = np.array(outputs)

    print("Input shape:", inputs.shape)
    print("Output shape:", outputs.shape)

    model = SolarLSTM(input_size=len(features))

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, factor=0.5, patience=3
    )