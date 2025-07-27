import threading
import pandas as pd
from datetime import datetime, timedelta
import random
import time

ohlcv = pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
lock = threading.Lock()

def get_ohlcv_df():
    with lock:
        return ohlcv.copy()


def start_kline_ws(symbol="SOL-USDT", interval="1m"):
    def mock_stream():
        global ohlcv
        base_price = 150.00
        while True:
            
            if ohlcv.empty:
                now = datetime.now().replace(second=0, microsecond=0)
            else:
                now = ohlcv.iloc[-1]["timestamp"] + timedelta(minutes=1)

            # Preload 20 mock candles efficiently
            rows = []
            for i in range(20):
                ts = now - timedelta(minutes=20 - i)
                price = 150 + random.uniform(-2, 2)
                rows.append([
                    ts,
                    float(price),
                    float(price + 0.3),
                    float(price - 0.3),
                    float(price),
                    float(random.uniform(50, 250))
                ])

            with lock:
                ohlcv = pd.concat([ohlcv, pd.DataFrame(rows, columns=ohlcv.columns)])


            price = base_price + random.uniform(-1.5, 1.5)
            high = price + random.uniform(0.1, 0.5)
            low = price - random.uniform(0.1, 0.5)
            open_ = price + random.uniform(-0.3, 0.3)
            close = price + random.uniform(-0.3, 0.3)
            volume = random.uniform(10, 300)

            row = {
                "timestamp": now,
                "open": round(open_, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "close": round(close, 2),
                "volume": round(volume, 2)
            }

            # 💣 Force breakout: inject a price clearly below historical lower band
            if len(ohlcv) > 19:
                ma = ohlcv['close'].rolling(window=20).mean().iloc[-1]
                std = ohlcv['close'].rolling(window=20).std().iloc[-1]
                lower_band = ma - 2 * std
                forced_close = round(lower_band - 2.0, 2)

                # Clamp to avoid unrealistic values
                if forced_close < 0:
                    forced_close = max(1.0, ma * 0.95)

                row["close"] = forced_close
                row["low"] = forced_close - 0.2
                row["high"] = forced_close + 0.3

                



            with lock:
                if not ohlcv.empty and ohlcv.iloc[-1]["timestamp"] == row["timestamp"]:
                    ohlcv.iloc[-1] = row
                else:
                    ohlcv = pd.concat([ohlcv, pd.DataFrame([row], columns=ohlcv.columns)])
                    ohlcv = ohlcv.tail(100)


            print("🔥 MOCK candle:", row)
            time.sleep(1)  # Feed every 5s to simulate rapid testing

    thread = threading.Thread(target=mock_stream)
    thread.daemon = True
    thread.start()
