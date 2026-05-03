
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from matplotlib import pyplot as plt

df_pvgis = pd.read_csv('duzce_2020_pvgis_hourly_data.csv')
df_open = pd.read_csv('duzce_2020_open_hourly_data.csv')

df = pd.merge(df_pvgis.sort_values('time'), 
              df_open.sort_values('time'), 
              on='time')

features = [
    "shortwave_radiation",
    "direct_normal_irradiance",
    "diffuse_radiation",
    "cloud_cover",
    "temperature_2m"
]

inputs = df[features]
outputs = df['power_watt']

model = RandomForestRegressor(n_estimators=100)
model.fit(inputs, outputs)

#feature importance
importance = pd.Series(model.feature_importances_, index=features)
print(importance.sort_values(ascending=False))

importance.sort_values().plot(kind="barh")
plt.xlabel("Feature Importance")
plt.ylabel("Features")
plt.title("Feature Importance in Random Forest Model")
plt.show()