import pandas as pd

df_pvgis = pd.read_csv('../duzce_2020_pvgis_hourly_data.csv')
df_open = pd.read_csv('../duzce_2020_open_hourly_data.csv')

# 1. Saat kolonlarını datetime formatına çevir (eğer metin şeklindeyse)
df_pvgis['time'] = pd.to_datetime(df_pvgis['time'])
df_open['time'] = pd.to_datetime(df_open['time'])

# 2. PVGIS verisine 3 SAAT EKLE (UTC -> UTC+3 geçişi)
df_pvgis['time'] = df_pvgis['time'] + pd.Timedelta(hours=3)

# 3. Verileri 'time' kolonu üzerinden birleştir (Inner join ile eşleşmeyen uç saatleri atarız)
df = pd.merge(df_open, df_pvgis, on='time', how='inner')

print(f"Yeni birleştirilen veri seti boyutu: {df.shape}")