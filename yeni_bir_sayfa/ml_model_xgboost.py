import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np
import joblib

df_pvgis = pd.read_csv('../duzce_2020_pvgis_hourly_data_kampus.csv')
df_open = pd.read_csv('../duzce_2020_open_hourly_data.csv')

df_pvgis['time'] = pd.to_datetime(df_pvgis['time'])
df_open['time'] = pd.to_datetime(df_open['time'])

df_pvgis['time'] = df_pvgis['time'] + pd.Timedelta(hours=3)

df = pd.merge(df_pvgis, 
            df_open, 
            on='time',
            how='inner')

df_gunduz = df[df['shortwave_radiation'] > 0].copy()

df_gunduz['time'] = pd.to_datetime(df_gunduz['time'])

df_gunduz['Saat'] = df_gunduz['time'].dt.hour
df_gunduz['Ay'] = df_gunduz['time'].dt.month

# df['time'] = pd.to_datetime(df['time'])

# df['Saat'] = df['time'].dt.hour
# df['Ay'] = df['time'].dt.month

hedef_kolon = 'power_kw'
dusecek_kolonlar = ['power_kw', 'power_watt', 'time', 'irradiance', 'temperature']

y = df_gunduz[hedef_kolon]
X = df_gunduz.drop(columns=dusecek_kolonlar)
# y = df[hedef_kolon]
# X = df.drop(columns=dusecek_kolonlar)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

xgb_model = xgb.XGBRegressor(
    n_estimators=100, 
    learning_rate=0.1, 
    random_state=42,
    objective='reg:squarederror' # Modelin regresyon yapacağını ve kare hatayı minimize edeceğini belirtiriz
)

print("XGBoost modeli eğitiliyor...")
xgb_model.fit(X_train, y_train)
print("Eğitim tamamlandı!")

xgb_y_pred = xgb_model.predict(X_test)

xgb_rmse = np.sqrt(mean_squared_error(y_test, xgb_y_pred))
xgb_r2 = r2_score(y_test, xgb_y_pred)

print("-" * 30)
print("--- XGBOOST MODEL PERFORMANSI ---")
print(f"RMSE (Kök Ortalama Kare Hata): {xgb_rmse:.2f} kW")
print(f"R² (Belirlilik Katsayısı)   : {xgb_r2:.4f}")

joblib.dump(xgb_model, 'xgboost_gunes_modelim_gunduz.pkl')

print("Model başarıyla kaydedildi!")