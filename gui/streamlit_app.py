
import streamlit as st
import pandas as pd
from core.strategy import calculate_bollinger_bands, generate_bollinger_signal
from features.stop_loss_take_profit import calculate_tp_sl, should_exit
import ccxt
import os
from dotenv import load_dotenv

load_dotenv()

symbol = 'SOL/USDT'
timeframe = '1m'
limit = 100

exchange = ccxt.binance({
    'apiKey': os.getenv("API_KEY"),
    'secret': os.getenv("API_SECRET"),
    'enableRateLimit': True,
})

def fetch_data():
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

st.set_page_config(page_title="Neetechs Bollibot-X", layout="wide")
st.title("📊 Neetechs Bollibot-X Dashboard")

df = fetch_data()
df = calculate_bollinger_bands(df)
signal = generate_bollinger_signal(df)
# Simulated position tracking (replace with live state/store if needed)
st.subheader("📌 Position Status")

# For now, simulate that we're in a LONG position (you can link to real logic later)
position_type = st.session_state.get("position_type", None)
entry_price = st.session_state.get("entry_price", None)

# Optionally set mock position (for testing)
col1, col2 = st.columns(2)
with col1:
    if st.button("🟢 Enter Long"):
        st.session_state["position_type"] = "long"
        st.session_state["entry_price"] = price

with col2:
    if st.button("🔴 Exit"):
        st.session_state.clear()

position_type = st.session_state.get("position_type", None)
entry_price = st.session_state.get("entry_price", None)

if position_type and entry_price:
    tp_price, sl_price = calculate_tp_sl(entry_price, position_type)
    st.success(f"✅ {position_type.upper()} from ${entry_price:.2f}")
    st.write(f"🎯 TP: `{tp_price}` | 🛑 SL: `{sl_price}`")
    
    if should_exit(position_type, price, tp_price, sl_price):
        st.error("🚨 TP/SL TRIGGERED — You should exit!")
else:
    st.info("No active position.")

price = df['close'].iloc[-1]

st.metric("📈 Current Price", f"${price:.2f}")
st.metric("📢 Last Signal", signal or "None")

with st.expander("📉 Price Chart + Bands"):
    st.line_chart(df[['close', 'sma', 'upper_band', 'lower_band']].set_index(df['timestamp']))

st.write("🧠 Bollinger Band Info")
st.dataframe(df.tail(5)[['timestamp', 'close', 'sma', 'upper_band', 'lower_band']])
import os
from datetime import datetime

st.subheader("📜 Trade Log")

log_path = os.path.join("logs", f"trades_{datetime.now().strftime('%Y-%m-%d')}.log")

if os.path.exists(log_path):
    with open(log_path, "r") as f:
        logs = f.readlines()
        logs = logs[-50:]  # show last 50 lines
        st.text("".join(logs))
else:
    st.warning("No logs found for today.")
