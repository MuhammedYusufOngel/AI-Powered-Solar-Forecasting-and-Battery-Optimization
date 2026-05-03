import pulp
import pandas as pd
import joblib
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error

import sqlite3
import time

prob = pulp.LpProblem("Batarya_Optimizasyonu", pulp.LpMinimize)

ham_veri = [6.29, 6.31, 6.21, 6.26, 6.29, 6.25, 6.25, 6.33, 6.31, 6.27, 6.36, 6.38, 
            6.27, 6.37, 6.48, 6.26, 6.30, 6.30, 6.39, 6.32, 6.27, 6.23, 6.39, 6.46]

katsayilar = [
    0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, # 00:00 - 06:00 (Gece bekleyen yük - Yaklaşık 2.5 kW)
    0.8, 0.8,                          # 07:00 - 08:00 (Sabah hareketliliği - Yaklaşık 5.0 kW)
    2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, # 09:00 - 16:00 (Mesai/Ders saati pik - Yaklaşık 12.6 kW)
    0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7  # 17:00 - 23:00 (Akşam kapanış - Yaklaşık 4.4 kW)
]


consumption = [ham * kat for ham, kat in zip(ham_veri, katsayilar)]

# 1. Veriyi okuma ve ilk 24 saati (Yarınki gün öncesini) alma
df = pd.read_csv("../duzce_2019_open_hourly_data.csv")
df = df[0:24].copy() 

# 2. Modeli Yükle
yuklenen_model = joblib.load("xgboost_model.pkl")

# 3. ZAMAN DÖNÜŞÜMLERİ (Modelin tanıdığı dile çeviriyoruz)
df['time'] = pd.to_datetime(df['time'])

df['Saat'] = df['time'].dt.hour
df['Ay'] = df['time'].dt.month

df['hour'] = df['time'].dt.hour
df['month'] = df['time'].dt.month

df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24.0)
df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24.0)
df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12.0)
df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12.0)

df['irradiance_lag1'] = df['direct_normal_irradiance'].shift(1).fillna(0) # 1 saat önceki ışınım
df['temp_lag1'] = df['temperature_2m'].shift(1).fillna(0) # 1 saat önceki sıcaklık
df['temp_rolling_3h'] = df['temperature_2m'].rolling(window=3).mean()

# 4. SADECE MODELİN İSTEDİĞİ SÜTUNLARI SEÇME
# Dikkat: Modeli hangi sırayla eğittiysen buradaki sıra aynı olmalı!
X_tahmin = df[['temperature_2m', 'cloud_cover', 'shortwave_radiation', 'direct_radiation', 'direct_normal_irradiance', 'diffuse_radiation', 'wind_speed_10m', 'precipitation', 'irradiance_lag1', 'temp_lag1', 'temp_rolling_3h', 'Saat', 'Ay']]

# 5. TAHMİNİ YAP (Sonuç bir NumPy array dönecek)
ham_tahminler = yuklenen_model.predict(X_tahmin)

# 6. GECE FİLTRESİ (Hackathon Kurtaran Hamle)
# Gece saatlerinde (irradiance == 0) modelin saçmalamasını önlemek için tahmini sıfıra eziyoruz.
temiz_tahminler = np.where(df['direct_normal_irradiance'] <= 0, 0, ham_tahminler)

# 7. Algoritmaya (PuLP) vereceğimiz o temiz Python listesine çevirme
solar_prediction = temiz_tahminler.tolist()

prices = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.2, 0.2, 0.2, 0.2, 0.2]

grid_buy = pulp.LpVariable.dicts("GridBuy", range(24), lowBound=0)
bat_charge = pulp.LpVariable.dicts("Charge", range(24), lowBound=0, upBound=50)
bat_discharge = pulp.LpVariable.dicts("Discharge", range(24), lowBound=0, upBound=50)
soc = pulp.LpVariable.dicts("SoC", range(25), lowBound=50, upBound=500)

prob += pulp.lpSum(grid_buy[t] * prices[t] for t in range(24))
baslangic_enerjisi = 60.0 

# Algoritmaya 0. saatteki doluluğun bu değere eşit olmak ZORUNDA olduğunu söylüyoruz
prob += (soc[0] == baslangic_enerjisi)

for t in range(24):
    prob += (consumption[t] == solar_prediction[t] + grid_buy[t] + bat_discharge[t] - bat_charge[t])

    prob += (soc[t+1] == soc[t] + bat_charge[t] - bat_discharge[t])

prob.solve()

saatler = list(range(24))

soc_degerleri = [soc[t].varValue if soc[t].varValue is not None else 0 for t in range(24)]
sarj_degerleri = [bat_charge[t].varValue if bat_charge[t].varValue is not None else 0 for t in range(24)]
desarj_degerleri = [bat_discharge[t].varValue if bat_discharge[t].varValue is not None else 0 for t in range(24)]

fig, axs = plt.subplots(3, 1, figsize=(12, 14))
fig.tight_layout(pad=6.0) # Grafikler birbirine yapışmasın diye boşluk bırakıyoruz

df_pvgis = pd.read_csv("../duzce_2019_pvgis_hourly_data_kampus.csv")
df_pvgis['time'] = pd.to_datetime(df_pvgis['time'])
df_pvgis['time'] = df_pvgis['time'] + pd.Timedelta(hours=3)

# 2. Open-Meteo (Hava Durumu) verisini oku
# (Dosya adını kendi prorendeki isme göre düzelt)
df_meteo = pd.read_csv("../duzce_2019_open_hourly_data.csv")
df_meteo['time'] = pd.to_datetime(df_meteo['time'])

# 3. İŞİN SIRRI BURADA: İki veriyi 'time' sütununda çakıştırıyoruz!
# how='inner' diyerek sadece her iki dosyada da karşılığı olan saatleri alıyoruz.
df_birlestirilmis = pd.merge(df_meteo, df_pvgis[['time', 'power_kw']], on='time', how='inner')

df_birlestirilmis = df_birlestirilmis["power_kw"].tolist()
df_birlestirilmis = [0.0, 0.0, 0.0] + df_birlestirilmis

df_birlestirilmis = df_birlestirilmis[0:24]

# 1. GRAFİK: Üretim ve Tüketim (Sorunun Kendisi)
# Not: 'solar_prediction' ve 'gercekci_kampus_tuketimi' listelerinin kodunda tanımlı olduğunu varsayıyorum
axs[0].plot(saatler, solar_prediction, label='Güneş Üretimi (Tahmin)', color='orange', linewidth=2, marker='o')
axs[0].plot(saatler, df_birlestirilmis, label='Güneş Üretimi (Gerçek)', color='green', linewidth=2, marker='o')
axs[0].plot(saatler, consumption, label='Kampüs Tüketimi', color='red', linewidth=2, linestyle='--')
axs[0].set_title('1. Temel Durum: Üretim ve Tüketim Eğrileri', fontsize=14, fontweight='bold')
axs[0].set_ylabel('Güç (kW)')
axs[0].set_xticks(saatler)
axs[0].legend()
axs[0].grid(True, alpha=0.3)

# 2. GRAFİK: Batarya Aksiyonları (Algoritmanın Çözümü)
axs[1].bar(saatler, sarj_degerleri, label='Batarya Şarj Oluyor (Güneş Fazlası)', color='green', alpha=0.7)
# Deşarjı grafikte aşağı doğru (eksi) göstermek için başına '-' koyuyoruz, daha şık durur
axs[1].bar(saatler, [-val for val in desarj_degerleri], label='Batarya Deşarj Oluyor (İhtiyaç Anı)', color='purple', alpha=0.7)
axs[1].set_title('2. Batarya Kararları: Hangi Saatte Ne Yaptı?', fontsize=14, fontweight='bold')
axs[1].set_ylabel('Güç (kW)')
axs[1].set_xticks(saatler)
axs[1].axhline(0, color='black', linewidth=1) # Tam ortaya 0 çizgisi
axs[1].legend()
axs[1].grid(True, alpha=0.3)

# 3. GRAFİK: Batarya Doluluk Oranı / SoC (Nihai Sonuç)
axs[2].plot(saatler, soc_degerleri, label='Batarya Doluluk Oranı (SoC)', color='blue', linewidth=3)
axs[2].axhline(50, color='red', linestyle=':', linewidth=2, label='Kritik Alt Sınır (50 kWh)')
axs[2].set_title('3. Sağlık Durumu: Batarya Kapasitesi (SoC)', fontsize=14, fontweight='bold')
axs[2].set_xlabel('Günün Saatleri (00:00 - 23:00)', fontsize=12)
axs[2].set_ylabel('Enerji (kWh)')
axs[2].set_xticks(saatler)
axs[2].legend()
axs[2].grid(True, alpha=0.3)

# Ekrana bas!
plt.show()

conn = sqlite3.connect("../Hackathon/GreenCodeHackathon/energy.db")
cursor = conn.cursor()

print("Veri tabanı bağlantısı başarılı! Sistem simülasyonu başlatılıyor...\n")
print("-" * 40)

maksimum_kapasite = max(df_birlestirilmis) if max(df_birlestirilmis) > 0 else 80.0

# 3. ZAMAN DÖNGÜSÜ (Şov Kısmı)
# 24 saati döngüye alıyoruz ve PuLP'un sonuçlarını tek tek çekiyoruz
for t in range(24):
    uretim = solar_prediction[t]
    tuketim = consumption[t]

    alinan_guc = grid_buy[t].varValue
    verilen_para = alinan_guc * prices[t]
    
    # varValue None dönerse diye güvenlik önlemi (0 yazdırıyoruz)
    sarj = bat_charge[t].varValue if bat_charge[t].varValue is not None else 0
    desarj = bat_discharge[t].varValue if bat_discharge[t].varValue is not None else 0
    doluluk = soc[t].varValue if soc[t].varValue is not None else 0

    time_val = df['time'][t+144].strftime('%Y-%m-%d %H:%M:%S')

    # 4. Veritabanına Gönder (Insert)

    if sarj == 0 and desarj == 0:
        cursor.execute('''
            INSERT INTO battery_status (timestamp, charge_percent, capacity_kwh, current_power_kw, decision, decision_reason, price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (time_val, 100 * doluluk/500, 500, 0, "IDLE", "Üretim-tüketim dengede", verilen_para))

        
    elif sarj == 0 and abs(desarj) > 0:
        cursor.execute('''
            INSERT INTO battery_status (timestamp, charge_percent, capacity_kwh, current_power_kw, decision, decision_reason, price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (time_val, 100 * doluluk/500, 500, -1 * desarj, "DISCHARGE", "Pik talep saati", verilen_para))
        
        
    elif abs(sarj) > 0 and desarj == 0:
        cursor.execute('''
            INSERT INTO battery_status (timestamp, charge_percent, capacity_kwh, current_power_kw, decision, decision_reason, price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (time_val, 100 * doluluk/500, 500, sarj, "CHARGE", "Yüksek güneş enerjisi üretimi", verilen_para))

    sapma_kw = abs(df_birlestirilmis[t] - uretim)

    sapma_yuzdesi = (sapma_kw / maksimum_kapasite) * 100
    guven = 100.0 - sapma_yuzdesi
    guven = max(0.0, guven)

    cursor.execute('''
            INSERT INTO energy_predictions (timestamp, predicted_kw, actual_kw, confidence, source, guven_skoru)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (time_val, uretim, df_birlestirilmis[t], sapma_yuzdesi, "Open-Mateo/PVGIS", guven))

    # Değişiklikleri kaydet
    conn.commit()
    
    # Terminalde nasıl aktığını görmek için bir log yazdırıyoruz
    print(f"[Saat {t:02d}:00] -> Üretim: {uretim:.1f} | Tüketim: {tuketim:.1f} | Batarya SoC: {doluluk:.1f} kWh -> DB'ye kaydedildi.")
    
    # İŞTE SİHİRLİ NOKTA: Döngüyü 1 saniye uyutuyoruz. 
    # Böylece jüriye sunarken veriler dashboard'a şak diye düşmez, saniye saniye anlık veri gibi akar!
    time.sleep(1)

print("-" * 40)
print("Tüm günün optimizasyon senaryosu başarıyla Dashboard'a iletildi!")

# Bağlantıyı kapat
conn.close()