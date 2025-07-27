# gui/streamlit_app.py
import streamlit as st
import pandas as pd
from core.strategy import calculate_bollinger_bands, generate_bollinger_signal
from core.apex_ws import get_ohlcv_df, preload_history, start_polling
import time
import threading
import numpy as np
from ta.momentum import RSIIndicator
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

if "wallet" not in st.session_state:
    st.session_state.wallet = 1000.0

# Start mock stream
preload_history()
start_polling()

st.set_page_config(page_title="Neetechs BolliBot X", layout="wide")
st.metric("💰 Wallet Balance (USD)", f"${st.session_state.wallet:.2f}")

# Input fields
st.sidebar.subheader("Bot Settings")
qty = st.sidebar.number_input("Quantity (SOL)", value=1.0, step=0.1)
tp_pct = st.sidebar.slider("Take Profit %", 0.1, 10.0, value=3.0)
sl_pct = st.sidebar.slider("Stop Loss %", 0.1, 10.0, value=1.0)
usd_to_sol = st.sidebar.number_input("USD to SOL Rate", value=150.0)
rsi_upper = st.sidebar.slider("RSI Overbought (Sell Above)", 50, 90, value=70)
rsi_lower = st.sidebar.slider("RSI Oversold (Buy Below)", 10, 50, value=30)

if "run_bot" not in st.session_state:
    st.session_state.run_bot = False

def toggle_bot():
    st.session_state.run_bot = not st.session_state.run_bot

st.sidebar.button("▶️ Start / 🛑 Stop Strategy", on_click=toggle_bot)

placeholder = st.empty()
status_box = st.sidebar.empty()
history_container = st.container()

position = None
entry_price = None
tp_price = None
sl_price = None
entry_time = None
entry_signal = None

trade_history = []
entry_logs = []
exit_logs = []

while st.session_state.run_bot:
    df = get_ohlcv_df()
    if len(df) < 21:
        placeholder.warning("Waiting for enough candles...")
        time.sleep(1)
        continue

    df = calculate_bollinger_bands(df)
    df['rsi'] = RSIIndicator(close=df['close'], window=14).rsi()

    latest = df.iloc[-1]
    previous = df.iloc[-2]
    signal = None

    if previous['close'] < previous['lower'] and latest['close'] > latest['lower'] and latest['rsi'] < rsi_lower:
        signal = 'buy'
    elif previous['close'] > previous['upper'] and latest['close'] < latest['upper'] and latest['rsi'] > rsi_upper:
        signal = 'sell'

    price = latest['close']

    with placeholder.container():
        st.subheader("Latest Candles")
        st.dataframe(df.tail(10).sort_values(by="timestamp", ascending=False))

        st.subheader("Candlestick Chart")

        last_df = df.tail(50)

        fig = go.Figure()

        # Candlesticks
        fig.add_trace(go.Candlestick(
            x=last_df['timestamp'],
            open=last_df['open'],
            high=last_df['high'],
            low=last_df['low'],
            close=last_df['close'],
            name="Price"
        ))

        # Bollinger Bands
        fig.add_trace(go.Scatter(
            x=last_df['timestamp'],
            y=last_df['upper'],
            line=dict(color='rgba(0, 255, 0, 0.5)', width=1),
            name='Upper Band'
        ))
        fig.add_trace(go.Scatter(
            x=last_df['timestamp'],
            y=last_df['lower'],
            line=dict(color='rgba(255, 0, 0, 0.5)', width=1),
            name='Lower Band'
        ))

        fig.update_layout(
            xaxis_rangeslider_visible=False,
            height=500,
            margin=dict(t=30, b=20),
            template="plotly_dark"
        )

        st.plotly_chart(fig, use_container_width=True, key=f"candles_{time.time()}")



        st.subheader("Current Status")
        st.write(f"**Last Close:** `{price:.2f}`")
        st.write(f"**RSI:** `{latest['rsi']:.2f}`")
        st.write(f"**Signal:** `{signal}`")
        st.write(f"**Position:** `{position}`")

    status_box.info(f"Close: {price:.2f} | RSI: {latest['rsi']:.2f} | Signal: {signal} | Position: {position}")

    if position is None and signal:
        position = signal
        entry_price = price
        tp_price = price * (1 + (tp_pct/100)) if signal == 'buy' else price * (1 - (tp_pct/100))
        sl_price = price * (1 - (sl_pct/100)) if signal == 'buy' else price * (1 + (sl_pct/100))
        entry_time = latest['timestamp']
        entry_signal = signal
        entry_logs.append({"Action": "BUY" if signal == 'buy' else "SELL", "Price": price, "Time": entry_time})

    elif position == 'buy' and (price >= tp_price or price <= sl_price):
        pnl = (price - entry_price) * qty * usd_to_sol
        st.session_state.wallet += pnl

        result = {
            "Direction": "LONG",
            "Entry": entry_price,
            "Exit": price,
            "TP": tp_price,
            "SL": sl_price,
            "PnL %": round(((price - entry_price) / entry_price) * 100, 2),
            "PnL $": round(pnl, 2),

            "Timestamp": latest['timestamp']
        }
        trade_history.append(result)
        exit_logs.append({"Action": "SELL (Exit)", "Price": price, "Time": latest['timestamp']})
        position = None

    elif position == 'sell' and (price <= tp_price or price >= sl_price):
        pnl = (entry_price - price) * qty * usd_to_sol
        st.session_state.wallet += pnl

        result = {
            "Direction": "SHORT",
            "Entry": entry_price,
            "Exit": price,
            "TP": tp_price,
            "SL": sl_price,
            "PnL %": round(((entry_price - price) / entry_price) * 100, 2),
            "PnL $": round(pnl, 2),

            "Timestamp": latest['timestamp']
        }
        trade_history.append(result)
        exit_logs.append({"Action": "BUY (Exit)", "Price": price, "Time": latest['timestamp']})
        position = None

    if trade_history:
        st.subheader("📜 Trade History")

        history_df = pd.DataFrame(trade_history[::-1])

        def color_pnl(val):
            if isinstance(val, (int, float)):
                return "color: green" if val > 0 else "color: red"
            return ""

        styled_df = history_df.style.applymap(color_pnl, subset=["PnL %", "PnL $"])
        st.dataframe(styled_df)


    if entry_logs or exit_logs:
        st.subheader("🧾 Entry/Exit Log")
        combined_logs = pd.DataFrame(entry_logs + exit_logs).sort_values(by="Time", ascending=False)
        st.dataframe(combined_logs)

    time.sleep(2)