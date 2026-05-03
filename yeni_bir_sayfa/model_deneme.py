import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

yuklenen_model = joblib.load("xgboost_gunes_modelim_gunduz.pkl")

df_pvgis = pd.read_csv('../duzce_2019_pvgis_hourly_data.csv')
df_open = pd.read_csv('../duzce_2019_open_hourly_data.csv')

df_open = df_open.drop(columns=['sira'])

df_pvgis['time'] = pd.to_datetime(df_pvgis['time'])
df_open['time'] = pd.to_datetime(df_open['time'])

df_pvgis['time'] = df_pvgis['time'] + pd.Timedelta(hours=3)

df = pd.merge(df_pvgis, 
            df_open, 
            on='time',
            how='inner')

# # 1. GEÇMİŞ ZAMAN ÖZELLİKLERİNİ (LAG FEATURES) HAM VERİDE ÜRETME
# df['Radyasyon_1_Saat_Once'] = df['shortwave_radiation'].shift(1)
# df['Sicaklik_1_Saat_Once'] = df['temperature_2m'].shift(1)

# # İlk satırın öncesi olmadığı için "NaN" (Boş) dönecektir. Modeli bozmaması için siliyoruz:
# df = df.dropna()

df_gunduz = df[df['shortwave_radiation'] > 0].copy()

df_gunduz['time'] = pd.to_datetime(df_gunduz['time'])

df_gunduz['Saat'] = df_gunduz['time'].dt.hour
df_gunduz['Ay'] = df_gunduz['time'].dt.month

# df['time'] = pd.to_datetime(df['time'])

# df['Saat'] = df['time'].dt.hour
# df['Ay'] = df['time'].dt.month

hedef_kolon = 'power_kw'
dusecek_kolonlar = ['power_kw', 'power_watt', 'time', 'irradiance', 'temperature']

y_2019_gercek = df_gunduz[hedef_kolon]
X_2019_test = df_gunduz.drop(columns=dusecek_kolonlar)
# y_2019_gercek = df[hedef_kolon]
# X_2019_test = df.drop(columns=dusecek_kolonlar)

y_2019_tahmin = yuklenen_model.predict(X_2019_test)

rmse_2019 = np.sqrt(mean_squared_error(y_2019_gercek, y_2019_tahmin))
r2_2019 = r2_score(y_2019_gercek, y_2019_tahmin)

print("--- 2019 OUT-OF-TIME (ZAMAN DIŞI) TEST SONUÇLARI ---")
print(f"RMSE (Hata Payı) : {rmse_2019:.2f} kW")
print(f"R² (Başarı Oranı): {r2_2019:.4f}")
