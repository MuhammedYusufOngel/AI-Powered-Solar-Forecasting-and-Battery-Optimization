import pandas as pd

df_1 = pd.read_csv("../duzce_2019_open_hourly_data.csv")
df_2 = pd.read_csv("../duzce_2020_open_hourly_data.csv")

result = pd.concat([df_2, df_1], ignore_index=True)

result = result.drop(columns=['sira'])

result.to_csv("duzce_open_hourly_data.csv", index=False)

print(result.head())

# df_1 = pd.read_csv("../duzce_2019_pvgis_hourly_data.csv")
# df_2 = pd.read_csv("../duzce_2020_pvgis_hourly_data.csv")

# result = pd.concat([df_2, df_1], ignore_index=True)

# result.to_csv("duzce_pvgis_hourly_data.csv", index=False)

# print(result.head())

df_toplam = pd.concat([df_1, df_2], ignore_index=True)

print(f"Toplam Satır Sayısı: {df_toplam.shape[0]}")