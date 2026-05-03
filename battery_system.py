
# def decide_action(predicted_production, battery_level, price):
#     if predicted_production < 50:
#         if battery_level < 40:
#             return "CHARGE (gridden al)"
#         else:
#             return "HOLD"
    
#     elif predicted_production > 150:
#         if battery_level > 80:
#             return "SELL (şebekeye sat)"
#         else:
#             return "CHARGE (güneşten)"
    
#     else:
#         return "HOLD"

battery_capacity = 100

def decide_action(predicted_production, battery_level, hour, balance):

    grid_draw_amount, grid_sell_amount = 0, 0
    price = get_price(hour)
    consumption = predict_consumption(hour)
    consumption /= 10
    predicted_production /= 6

    net_energy = predicted_production - consumption

    if net_energy < 0:
        if battery_level <= 20:
            # grid_draw_amount = grid_draw(net_energy, battery_level)
            balance -= grid_draw_amount * price
            print(f"Drawing {grid_draw_amount} from grid at price {price}, new balance: {balance}")
            return update_battery(battery_level, net_energy+grid_draw_amount), balance
            return "BUY FROM GRID"
        
        elif battery_level > 20 and battery_level <= 60:
            if price < 1.0:
                # grid_draw_amount = grid_draw(net_energy, battery_level)
                balance -= grid_draw_amount * price
                print(f"Drawing {grid_draw_amount} from grid at price {price}, new balance: {balance}")
                return update_battery(battery_level, net_energy+grid_draw_amount), balance
                return "BUY FROM GRID"
            
            else:
                return update_battery(battery_level, net_energy), balance
                return "DISCHARGE BATTERY"
        
        elif battery_level > 60:
            return update_battery(battery_level, net_energy), balance
            return "DISCHARGE BATTERY"
    
    elif net_energy > 0:
        
        if battery_level <= 50:
            return update_battery(battery_level, net_energy), balance
            return "CHARGE BATTERY"
        
        elif battery_level > 50 and battery_level < 100:
            if price > 1.5:
                #grid_sell_amount = grid_sell(net_energy, battery_level)
                balance += grid_sell_amount * price
                print(f" Selling {grid_sell_amount} to grid at price {price}, new balance: {balance}")
                return update_battery(battery_level, net_energy-grid_sell_amount), balance
                return "SELL TO GRID"
            
            else:
                return update_battery(battery_level, net_energy), balance
                return "CHARGE BATTERY"
        
        elif battery_level == 100:
            #grid_sell_amount = grid_sell(net_energy, battery_level)
            balance += grid_sell_amount * price
            print(f" Selling {grid_sell_amount} to grid at price {price}, new balance: {balance}")
            return update_battery(battery_level, net_energy-grid_sell_amount), balance
            return "SELL TO GRID"

    else:
        return update_battery(battery_level, net_energy), balance
        return "HOLD"

def get_price(hour):
    if 18 <= hour <= 23:
        return 2.0  # peak saat (pahalı)
    elif 8 <= hour <= 17:
        return 1.2  # normal
    else:
        return 0.6  # gece ucuz
    
def predict_consumption(hour):
    if 18 <= hour <= 23:
        return 80   # peak usage
    elif 8 <= hour <= 17:
        return 50
    else:
        return 30
    
def update_battery(battery, net_energy):

    battery = battery + net_energy

    # sınırlar
    battery = max(0, min(battery_capacity, battery))

    return battery

def grid_draw(net_energy, battery):

    if net_energy >= 0:
        return 0  # gerek yok
    
    deficit = abs(net_energy)

    if battery > 20:
        return min(deficit, 10)   # az grid kullan
    
    elif battery > 5:
        return min(deficit, 30)   # orta destek
    
    else:
        return min(deficit, 60)   # full grid backup
    
def grid_sell(net_energy, battery):

    if net_energy <= 0:
        return 0  # gerek yok
    
    if battery >= 100:
        return net_energy  # tüm fazlalığı sat
    
    elif battery > 70:
        return net_energy * 0.8  # fazla kısmı sat, birazını depola
    
    else:
        return net_energy * 0.5  # az fazlalık, yarısını sat, yarısını depola