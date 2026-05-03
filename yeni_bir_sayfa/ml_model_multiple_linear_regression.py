import pandas as pd
from sklearn.model_selection import train_test_split

df_pvgis = pd.read_csv("../duzce_2020_pvgis_hourly_data_kampus.csv")

hedef_kolon = "power_kw"

dusecek_kolonlar = ["time", "power_watt", "irradiance", "temperature"]

y = df_pvgis[hedef_kolon]
X = df_pvgis.drop(columns=dusecek_kolonlar)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"Eğitim seti X boyutu: {X_train.shape}")
print(f"Test seti X boyutu: {X_test.shape}")