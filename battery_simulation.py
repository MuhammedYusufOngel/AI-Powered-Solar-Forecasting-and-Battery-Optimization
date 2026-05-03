import time

from battery_system import decide_action, get_price, predict_consumption
from open_mateo_model import model, df, X_test, hours, features

battery = 50
capacity = 100
balance = 500

print(X_test.columns)

for t in range(len(df)):

    predicted_prod = model.predict(df[features].iloc[t:t+1])[0]

    print(f"Hour: {t%24}, Predicted Production: {predicted_prod}, Consumption: {predict_consumption(t%24)}, Net Energy: {predicted_prod - predict_consumption(t%24)}, Battery Level: {battery}, Price: {get_price(t%24)}")

    battery, balance = decide_action(predicted_prod, battery, t%24, balance)
    time.sleep(1)