import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

from battery_system import decide_action, get_price

# CSV yükle
df = pd.read_csv("data_with_production.csv")

# Feature ve target
features = [
    "temperature_2m",
    "cloud_cover",
    "shortwave_radiation",
    "direct_radiation",
    "diffuse_radiation"
]

X = df[features]
y = df["production"]
df['time'] = pd.to_datetime(df['time'])

df['date'] = df['time'].dt.date
df['hour_only'] = df['time'].dt.hour

hours = df['hour_only']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Model
model = RandomForestRegressor(n_estimators=100)
model.fit(X_train, y_train)

# Tahmin
preds = model.predict(X_test)

# Basit değerlendirme
mae = mean_absolute_error(y_test, preds)
print("MAE:", mae)

sample = X_test.iloc[0:15]
prediction = model.predict(sample)

# for i in range(15):
#     pred = prediction[i]
#     hour = hours.iloc[i]
#     print(f"Gerçek: {y_test.iloc[i]:.2f}, Tahmin: {prediction[i]:.2f}, Saat: {hour}, battery_level: 90%")
#     action = decide_action(pred, battery_level=90, price=get_price(hour))

#     print("Tahmin edilen üretim:", pred)
#     print("Karar:", action)