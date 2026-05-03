import pandas as pd
import numpy as np

from sklearn.preprocessing import MinMaxScaler
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
import ml_model_ltsm as ltsm
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score

from torch.optim.lr_scheduler import ReduceLROnPlateau

def create_sequences(X, y, seq_len=24):
    Xs, ys = [], []
    for i in range(len(X) - seq_len):
        Xs.append(X[i:i+seq_len])
        ys.append(y[i+seq_len])
    return np.array(Xs), np.array(ys)

df_pvgis = pd.read_csv('duzce_2020_pvgis_hourly_data.csv')
df_open = pd.read_csv('duzce_2020_open_hourly_data.csv')

df = pd.merge(df_pvgis.sort_values('time'), 
            df_open.sort_values('time'), 
            on='time')

df = df.sort_values("time")

n = len(df)

lags = [1, 2, 3, 6, 12, 24]

for l in lags:
    df[f'irradiance_lag_{l}'] = df['direct_normal_irradiance'].shift(l)
    df[f'cloud_lag_{l}'] = df['cloud_cover'].shift(l)
    df[f'temp_lag_{l}'] = df['temperature_2m'].shift(l)

windows = [3, 6, 12, 24]

for w in windows:
    df[f'irradiance_mean_{w}'] = df['direct_normal_irradiance'].rolling(w).mean()
    df[f'irradiance_std_{w}'] = df['direct_normal_irradiance'].rolling(w).std()
    
    df[f'cloud_mean_{w}'] = df['cloud_cover'].rolling(w).mean()
    df[f'temp_mean_{w}'] = df['temperature_2m'].rolling(w).mean()


df['cloud_change'] = df['cloud_cover'].diff()
df['cloud_acceleration'] = df['cloud_change'].diff()

df = df.dropna()

df["time"] = pd.to_datetime(df["time"])
df["hour"] = df["time"].dt.hour
df["day_of_year"] = df["time"].dt.dayofyear

df['season_sin'] = np.sin(2*np.pi*df['day_of_year']/365)
df['season_cos'] = np.cos(2*np.pi*df['day_of_year']/365)

df['temp_ema_6'] = df['temperature_2m'].ewm(span=6).mean()
df['temp_ema_12'] = df['temperature_2m'].ewm(span=12).mean()

train_size = int(n * 0.7)
val_size = int(n * 0.15)

train_df = df[:train_size]
val_df = df[train_size:train_size + val_size]
test_df = df[train_size + val_size:]

features = [
    "direct_normal_irradiance",
    "shortwave_radiation",
    "temperature_2m",
    "cloud_cover",
    "cloud_change",
    "cloud_acceleration",
    "season_sin",
    "season_cos",
    "temp_ema_6",
    "temp_ema_12"
]

target = "power_watt"

scaler_x = MinMaxScaler()
scaler_y = MinMaxScaler()

train_x = scaler_x.fit_transform(train_df[features])
val_x = scaler_x.transform(val_df[features])
test_x = scaler_x.transform(test_df[features])

train_y = scaler_y.fit_transform(train_df[[target]])
val_y = scaler_y.transform(val_df[[target]])
test_y = scaler_y.transform(test_df[[target]])

X_train, y_train = create_sequences(train_x, train_y)
X_val, y_val = create_sequences(val_x, val_y)
X_test, y_test = create_sequences(test_x, test_y)

train_loader = DataLoader(
    TensorDataset(
        torch.tensor(X_train, dtype=torch.float32),
        torch.tensor(y_train, dtype=torch.float32)
    ),
    batch_size=32,
    shuffle=False  # ⚠ time series = False
)

model = ltsm.SolarLSTM(input_size=len(features))

optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = nn.MSELoss()

for epoch in range(20):
    model.train()
    total_loss = 0
    
    running_loss, correct, total = 0.0, 0, 0
    
    for X_batch, y_batch in train_loader:
        optimizer.zero_grad()
        
        output = model(X_batch)
        loss = criterion(output, y_batch)
        
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        
        running_loss += loss.item() * X_batch.size(0)
        _, predicted = torch.max(output, 1)
        total += y_batch.size(0)
        correct += (predicted == y_batch).sum().item()

    model.eval()
    
    with torch.no_grad():
        val_pred = model(torch.tensor(X_val, dtype=torch.float32))
        val_loss = criterion(val_pred, torch.tensor(y_val, dtype=torch.float32))
    
    with torch.no_grad():
        test_pred = model(torch.tensor(X_test, dtype=torch.float32))
        test_loss = criterion(test_pred, torch.tensor(y_test, dtype=torch.float32))
        
    final_pred = 0.6 * lstm_pred + 0.4 * xgb_pred

    pred, real = test_pred.numpy(), y_test

    pred = scaler_y.inverse_transform(pred)
    real = scaler_y.inverse_transform(y_test)
    
    mae = mean_absolute_error(real, pred)
    r2 = r2_score(real, pred)

    print(f"Epoch {epoch}: {total_loss:.4f} | Val Loss: {val_loss.item():.4f} | Test Loss: {test_loss.item():.4f} | MAE: {mae:.4f} | R2: {r2:.4f}")


    # pred = model(X_test)
    # mae = mean_absolute_error(y_test, pred)
    # print(mae)
    
    # print(r2_score(y_test, pred))

    