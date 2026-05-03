import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

pvgis_data = "../duzce_2020_pvgis_hourly_data_kampus.csv"
open_data = "../duzce_2020_open_hourly_data.csv"

df_pvgis = pd.read_csv(pvgis_data)
df_open = pd.read_csv(open_data)

df_pvgis['time'] = pd.to_datetime(df_pvgis['time'])
df_open['time'] = pd.to_datetime(df_open['time'])

df_pvgis['time'] = df_pvgis['time'] + pd.Timedelta(hours=3)

df = pd.merge(df_pvgis, 
            df_open, 
            on='time',
            how='inner')

df_gunduz = df[df['shortwave_radiation'] > 0].copy()

hedef_kolon = 'power_kw'
dusecek_kolonlar = ['power_kw', 'power_watt', 'time', 'irradiance', 'temperature']

y = df_gunduz[hedef_kolon]
X = df_gunduz.drop(columns=dusecek_kolonlar)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print(f"Filtrelenmiş Veri Seti Boyutu: {df_gunduz.shape[0]} satır")
print("-" * 30)
print("BAZ MODEL PERFORMANSI (Linear Regression):")
print(f"RMSE (Kök Ortalama Kare Hata): {rmse:.2f} kW")
print(f"R² (Belirlilik Katsayısı)   : {r2:.4f}")