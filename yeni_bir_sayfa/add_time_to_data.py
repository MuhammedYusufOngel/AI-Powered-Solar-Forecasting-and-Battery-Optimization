import pandas as pd

df_2019 = pd.read_csv("../duzce_2026_open_hourly_data.csv")

zaman_dizisi = pd.date_range(start='2026-01-01 00:00:00', 
                             end='2026-05-02 23:00:00', 
                             freq='h')

# 2. ÖNEMLİ KONTROL: Veri setin tam 8760 satır mı?
print(f"Oluşturulan saat sayısı: {len(zaman_dizisi)}")
print(f"2026 verindeki satır sayısı: {len(df_2019)}")

# 3. Eğer sayılar eşleşiyorsa, bu diziyi veri setine 'time' kolonu olarak ata
if len(zaman_dizisi) == len(df_2019):
    df_2019['time'] = zaman_dizisi
    df_2019.to_csv("../duzce_2026_open_hourly_data.csv")
    print("Zaman kolonu başarıyla eklendi!")
else:
    print("DİKKAT: Veri setindeki satır sayısı ile 1 yıllık saat sayısı uyuşmuyor!")