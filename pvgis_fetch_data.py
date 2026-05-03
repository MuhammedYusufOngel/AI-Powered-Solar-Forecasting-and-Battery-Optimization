import requests
import pandas as pd

url = "https://re.jrc.ec.europa.eu/api/v5_2/seriescalc"
params = {
    "lat": 40.8387,
    "lon": 31.1626,

    # 🔥 BUNLAR ŞART
    "pvcalculation": 1,
    "peakpower": 250,
    "loss": 14,
    "outputformat": "json",
    "startyear": 2020,
    "endyear": 2020
}

res = requests.get(url, params=params)
data = res.json()

if "outputs" not in data:
    print("API hata döndü:", data)
    exit()

hourly = data["outputs"]["hourly"]

print(hourly[:5])

df = pd.DataFrame(hourly)

df["time"] = pd.to_datetime(df["time"], format="%Y%m%d:%H%M")

df = df.rename(columns={
    "P": "power_watt",
    "G(i)": "irradiance",
    "T2m": "temperature"
})

df = df[["time", "power_watt", "irradiance", "temperature"]]

df["power_kw"] = df["power_watt"] / 1000
df["time"] = df["time"] - pd.Timedelta(minutes=10)

df.to_csv("duzce_2020_pvgis_hourly_data_kampus.csv", index=False)

print(df.head())