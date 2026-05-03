import pandas as pd

# 1. Veriyi yükleme (Örnek olarak 'hava_durumu.csv' dosyasından okuduğumuzu varsayıyoruz)
# Kendi dosya adınıza göre burayı güncelleyebilirsiniz.
df = pd.read_csv('duzce_data_2026.csv')

# 2. 'production' sütununu hesaplama ve ekleme
# Pandas'ın vektörel işlemleri sayesinde tüm satırlar tek seferde hızlıca hesaplanır.
df['production'] = (
    (0.6 * df['shortwave_radiation'] + 
     0.3 * df['direct_radiation'] + 
     0.1 * df['diffuse_radiation']) 
    * (1 - df['cloud_cover'] / 100)
)

# Negatif üretim değerleri olmaması için (radyasyon sensör hatalarına karşı) 
# 0'ın altındaki değerleri 0'a eşitlemek iyi bir pratiktir (Opsiyonel)
df['production'] = df['production'].clip(lower=0)

# 3. İlk 5 satırı kontrol amaçlı yazdırma
print(df[['time', 'cloud_cover', 'shortwave_radiation', 'production']].head())

# 4. Yeni veriyi kaydetme
df.to_csv('duzce_data_with_production_2026.csv', index=False)
print("Yeni veri seti başarıyla kaydedildi!")