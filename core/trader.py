
import ccxt
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")

exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
})

symbol = 'SOL/USDT'
amount = 1.0  # 1 SOL

def place_order(signal):
    if signal == 'buy':
        order = exchange.create_market_buy_order(symbol, amount)
        print("🟢 LONG executed:", order)
    elif signal == 'sell':
        order = exchange.create_market_sell_order(symbol, amount)
        print("🔴 SHORT executed:", order)
    elif signal == 'exit_long':
        order = exchange.create_market_sell_order(symbol, amount)
        print("⬅️ EXIT LONG:", order)
    elif signal == 'exit_short':
        order = exchange.create_market_buy_order(symbol, amount)
        print("➡️ EXIT SHORT:", order)
    else:
        print("No action taken.")
