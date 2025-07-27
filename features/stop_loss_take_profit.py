def calculate_tp_sl(entry_price, position, tp_ratio=0.01, sl_ratio=0.005):
    if position == 'long':
        return entry_price * (1 + tp_ratio), entry_price * (1 - sl_ratio)
    elif position == 'short':
        return entry_price * (1 - tp_ratio), entry_price * (1 + sl_ratio)
    return None, None

def should_exit(position, current_price, tp, sl):
    if position == 'long' and (current_price >= tp or current_price <= sl):
        return True
    if position == 'short' and (current_price <= tp or current_price >= sl):
        return True
    return False