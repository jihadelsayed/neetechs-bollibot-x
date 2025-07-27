import asyncio
import websockets
import json
import pandas as pd
from datetime import datetime
import threading
import time

ohlcv = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

def get_ohlcv_df():
    return ohlcv.copy()

def start_kline_ws(symbol="SOL-USDT", interval="1m"):
    def run_loop():
        asyncio.run(_run_ws(symbol, interval))

    t = threading.Thread(target=run_loop)
    t.daemon = True
    t.start()

async def _run_ws(symbol="SOL-USDT", interval="1m"):
    global ohlcv
    uri = "wss://api.omni.apex.exchange/ws/v3"

    while True:
        try:
            async with websockets.connect(uri) as ws:
                sub_msg = {
                    "type": "subscribe",
                    "channel": "candles",
                    "instId": symbol,
                    "interval": interval
                }
                await ws.send(json.dumps(sub_msg))
                print(f"✅ Subscribed to {symbol} candles @ {interval}")

                async for msg in ws:
                    print("📥 RAW MSG:", msg)
                    try:
                        data = json.loads(msg)

                        if data.get("channel") == "candles" and "data" in data:
                            candle = data["data"]
                            row = {
                                "timestamp": datetime.fromtimestamp(candle["start"] / 1000),
                                "open": float(candle["open"]),
                                "high": float(candle["high"]),
                                "low": float(candle["low"]),
                                "close": float(candle["close"]),
                                "volume": float(candle["volume"]),
                            }

                            if not ohlcv.empty and ohlcv.iloc[-1]['timestamp'] == row['timestamp']:
                                ohlcv.iloc[-1] = row
                            else:
                                ohlcv = pd.concat([ohlcv, pd.DataFrame([row])])
                                ohlcv = ohlcv.tail(100)

                            print("📈 Candle received:", row)

                    except Exception as e:
                        print("❌ Parse error:", e)

        except Exception as e:
            print("❌ WebSocket error:", e)
            await asyncio.sleep(5)
