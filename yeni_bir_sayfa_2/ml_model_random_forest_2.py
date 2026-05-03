import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

df_pvgis = pd.read_csv('../duzce_2020_pvgis_hourly_data_kampus.csv')
df_open = pd.read_csv('../duzce_2020_open_hourly_data.csv')

df_pvgis['time'] = pd.to_datetime(df_pvgis['time'])
df_open['time'] = pd.to_datetime(df_open['time'])

df_pvgis['time'] = df_pvgis['time'] + pd.Timedelta(hours=3)

df = pd.merge(df_pvgis, 
            df_open, 
            on='time',
            how='inner')

df['irradiance_lag1'] = df['irradiance'].shift(1).fillna(0) # 1 saat önceki ışınım
df['temp_lag1'] = df['temperature'].shift(1).fillna(0) # 1 saat önceki sıcaklık

df_gunduz = df[df['irradiance'] > 0]

# Eğer zaman sütunun 'time' ise, önce onu datetime yapalım (zaten öyleyse bu satırı atlayabilirsin)
df['time'] = pd.to_datetime(df['time'])

# Saat ve Ay bilgilerini çekelim
df['hour'] = df['time'].dt.hour
df['month'] = df['time'].dt.month

# Sihirli dokunuş: Saati ve Ayı sinüs/kosinüs dalgalarına çeviriyoruz
df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24.0)
df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24.0)

df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12.0)
df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12.0)

# Artık düz 'hour' ve 'month' sütunlarına ihtiyacımız yok, silebiliriz
df = df.drop(['hour', 'month'], axis=1)

hedef_kolon = 'power_kw'
dusecek_kolonlar = ['power_kw', 'power_watt', 'time', 'irradiance', 'temperature', 'hour_sin', 'hour_cos', 'month_sin', 'month_cos']

y = df_gunduz[hedef_kolon]
X = df_gunduz.drop(columns=dusecek_kolonlar)
# y = df[hedef_kolon]
# X = df.drop(columns=dusecek_kolonlar)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

rf_model = RandomForestRegressor(n_estimators=100, random_state=42)

rf_model.fit(X_train, y_train)

rf_y_pred = rf_model.predict(X_test)

rf_rmse = np.sqrt(mean_squared_error(y_test, rf_y_pred))
rf_r2 = r2_score(y_test, rf_y_pred)

print("--- RANDOM FOREST MODEL PERFORMANSI ---")
print(f"RMSE (Kök Ortalama Kare Hata): {rf_rmse:.2f} kW")
print(f"R² (Belirlilik Katsayısı)   : {rf_r2:.4f}")