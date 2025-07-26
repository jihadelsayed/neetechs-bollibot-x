
import os

# These can later come from config or environment
TP_PERCENT = float(os.getenv("TP_PERCENT", 1.5))  # % profit
SL_PERCENT = float(os.getenv("SL_PERCENT", 1.0))  # % loss

def calculate_tp_sl(entry_price, position_type):
    """
    Given entry price and position type, returns TP and SL targets.
    """
    tp = None
    sl = None

    if position_type == 'long':
        tp = entry_price * (1 + TP_PERCENT / 100)
        sl = entry_price * (1 - SL_PERCENT / 100)
    elif position_type == 'short':
        tp = entry_price * (1 - TP_PERCENT / 100)
        sl = entry_price * (1 + SL_PERCENT / 100)

    return round(tp, 2), round(sl, 2)

def should_exit(position_type, current_price, tp_price, sl_price):
    """
    Returns True if TP or SL is hit.
    """
    if position_type == 'long':
        return current_price >= tp_price or current_price <= sl_price
    elif position_type == 'short':
        return current_price <= tp_price or current_price >= sl_price
    return False
