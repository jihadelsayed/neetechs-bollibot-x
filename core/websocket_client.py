import websocket
import json
import threading
import pandas as pd
from datetime import datetime

ohlcv_df = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

def on_message(ws, message):
    global ohlcv_df
    data = json.loads(message)

    kline = data['k']
    timestamp = datetime.fromtimestamp(kline['t'] / 1000)
    open_price = float(kline['o'])
    high = float(kline['h'])
    low = float(kline['l'])
    close = float(kline['c'])
    volume = float(kline['v'])

    new_row = {
        'timestamp': timestamp,
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    }

    # Update last row or append
    if not ohlcv_df.empty and ohlcv_df.iloc[-1]['timestamp'] == timestamp:
        ohlcv_df.iloc[-1] = new_row
    else:
        ohlcv_df = pd.concat([ohlcv_df, pd.DataFrame([new_row])])
        if len(ohlcv_df) > 100:
            ohlcv_df = ohlcv_df.iloc[-100:]

def on_error(ws, error):
    print("WebSocket Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket Closed")

def on_open(ws):
    print("✅ WebSocket Connected")

def start_kline_ws(symbol="solusdt", interval="1m"):
    url = f"wss://stream.binance.com:9443/ws/{symbol}@kline_{interval}"
    ws = websocket.WebSocketApp(url,
                                 on_message=on_message,
                                 on_error=on_error,
                                 on_close=on_close,
                                 on_open=on_open)
    thread = threading.Thread(target=ws.run_forever)
    thread.daemon = True
    thread.start()

def get_ohlcv_df():
    return ohlcv_df.copy()
