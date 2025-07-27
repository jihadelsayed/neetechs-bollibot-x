# core/trader.py

def place_order(signal):
    if signal == 'buy':
        print("📈 MOCK ORDER PLACED: BUY")
    elif signal == 'sell':
        print("📉 MOCK ORDER PLACED: SELL")
    elif signal == 'exit_long':
        print("🏁 MOCK ORDER EXIT: LONG CLOSED")
    elif signal == 'exit_short':
        print("🏁 MOCK ORDER EXIT: SHORT CLOSED")
    else:
        print(f"❓ Unknown signal: {signal}")
