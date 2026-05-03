import requests
import pandas as pd

def fetch_solar_weather_data(lat, lon, start_date, end_date):
    """
    Open-Meteo Archive API'sinden ML eğitimi için güneş ve hava durumu verilerini çeker.
    """
    # Model eğitimi için geçmiş veri API'si
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    # ML modelin ve karar motorun için konuştuğumuz kritik parametreler
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": [
            "temperature_2m",             # Verimlilik düşüşünü hesaplamak için
            "cloud_cover",                # Radyasyon engelleme faktörü
            "shortwave_radiation",        # GHI - Toplam Radyasyon (Ana üretim girdisi)
            "direct_radiation",           # Doğrudan ışınım
            "direct_normal_irradiance",   # DNI
            "diffuse_radiation",          # DHI - Saçılan ışınım
            "wind_speed_10m",             # Panel soğutma etkisi
            "precipitation"               # Batarya koruma stratejisi için (Yağış)
        ],
        "timezone": "auto" # Zaman dilimini lokasyona göre otomatik ayarla
    }

    try:
        print(f"Veriler çekiliyor... ({start_date} - {end_date})")
        response = requests.get(url, params=params)
        response.raise_for_status() # HTTP hatalarını yakala
        
        data = response.json()
        
        # 'hourly' sözlüğünü doğrudan Pandas DataFrame'e çeviriyoruz
        df = pd.DataFrame(data['hourly'])
        
        # 'time' sütununu datetime formatına çevirip index yapıyoruz
        df['time'] = pd.to_datetime(df['time'])
        df.set_index('time', inplace=True)
        
        # Eksik verileri (NaN) doldurma (İsteğe bağlı, veriye göre method değişebilir)
        df.ffill(inplace=True) 
        
        print("Veri başarıyla çekildi ve DataFrame'e dönüştürüldü!")
        return df

    except requests.exceptions.RequestException as e:
        print(f"API isteği sırasında hata oluştu: {e}")
        return None

# --- ÖRNEK KULLANIM ---

# Düzce Koordinatları
LATITUDE = 40.8387
LONGITUDE = 31.1626
START_DATE = "2026-01-01"
END_DATE = "2026-05-02"

# Fonksiyonu çağır
solar_df = fetch_solar_weather_data(LATITUDE, LONGITUDE, START_DATE, END_DATE)

if solar_df is not None:
    # Verinin ilk 5 satırına ve temel istatistiklerine bakalım
    print("\n--- Veri Seti Başlangıcı ---")
    print(solar_df.head())
    
    print("\n--- Veri Seti Bilgileri ---")
    print(solar_df.info())
    
    # Veriyi Federated Learning nodelarında kullanmak üzere CSV olarak kaydet
    solar_df.to_csv("duzce_2026_open_hourly_data.csv", index=False)