from apexomni.http_public import HttpPublic
from apexomni.constants import APEX_OMNI_HTTP_MAIN
import pandas as pd
from datetime import datetime
import threading

ohlcv = pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
lock = threading.Lock()

client = HttpPublic(APEX_OMNI_HTTP_MAIN)
client.configs_v3()  # preload symbols
import asyncio
import time
def get_ohlcv_df():
    with lock:
        return ohlcv.copy()

def preload_history(limit=100):
    resp = client.klines_v3(symbol="SOLUSDT", interval=1, limit=limit)
    rows = []
    klines = resp["data"]["SOLUSDT"]

    for k in klines:
        ts = datetime.fromtimestamp(k["t"] / 1000)
        rows.append({
            "timestamp": ts,
            "open": float(k["o"]),
            "high": float(k["h"]),
            "low": float(k["l"]),
            "close": float(k["c"]),
            "volume": float(k["v"]),
        })
    global ohlcv
    with lock:
        ohlcv = pd.DataFrame(rows).tail(100)

import traceback

def start_polling():
    def poll_loop():
        while True:
            try:
                resp = client.klines_v3(symbol="SOLUSDT", interval=1, limit=1)
                k = resp["data"]["SOLUSDT"][-1]

                print("🔍 resp =", type(resp), resp)

                ts = datetime.fromtimestamp(k["t"] / 1000)
                row = {
                    "timestamp": ts,
                    "open": float(k["o"]),
                    "high": float(k["h"]),
                    "low": float(k["l"]),
                    "close": float(k["c"]),
                    "volume": float(k["v"]),
                }

                with lock:
                    global ohlcv
                    if not ohlcv.empty and ohlcv.iloc[-1]["timestamp"] == row["timestamp"]:
                        ohlcv.iloc[-1] = row
                    else:
                        ohlcv = pd.concat([ohlcv, pd.DataFrame([row])])
                        ohlcv = ohlcv.tail(100)

                print("🔥 LIVE candle:", row)
                #time.sleep(60)
                time.sleep(5)

            except Exception as e:
                print("⚠️ Polling error:", e)
                traceback.print_exc()
                time.sleep(5)


    thread = threading.Thread(target=poll_loop)
    thread.daemon = True
    thread.start()