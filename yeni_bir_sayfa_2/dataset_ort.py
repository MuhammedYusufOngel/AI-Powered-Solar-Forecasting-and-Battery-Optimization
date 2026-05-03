ham_veri = [6.29, 6.31, 6.21, 6.26, 6.29, 6.25, 6.25, 6.33, 6.31, 6.27, 6.36, 6.38, 
            6.27, 6.37, 6.48, 6.26, 6.30, 6.30, 6.39, 6.32, 6.27, 6.23, 6.39, 6.46]

# KAMPÜS PROFİLİ KATSAYILARI (Sihirli Dokunuş)
# Mantık: Gece ölü zaman (0.4x), Sabah uyanış (0.8x), Öğlen pik zamanı (2.0x), Akşam mesai bitimi (0.7x)
katsayilar = [
    0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, # 00:00 - 06:00 (Gece bekleyen yük - Yaklaşık 2.5 kW)
    0.8, 0.8,                          # 07:00 - 08:00 (Sabah hareketliliği - Yaklaşık 5.0 kW)
    2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, # 09:00 - 16:00 (Mesai/Ders saati pik - Yaklaşık 12.6 kW)
    0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7  # 17:00 - 23:00 (Akşam kapanış - Yaklaşık 4.4 kW)
]

# İki listeyi çarpıp gerçekçi kampüs yükünü oluşturuyoruz
gercekci_kampus_tuketimi = [ham * kat for ham, kat in zip(ham_veri, katsayilar)]

# Artık PuLP optimizasyonunda consumption[t] olarak bu yeni listeyi kullanacaksın!
print(gercekci_kampus_tuketimi)