from features.stop_loss_take_profit import calculate_tp_sl, should_exit
from features.discord_alerts import send_alert
from features.logger import log_trade
from core.apex_ws import preload_history, start_polling, get_ohlcv_df
from core.trader import place_order
from core.strategy import calculate_bollinger_bands, generate_bollinger_signal
import time

position = None  # 'long' or 'short'
entry_price = None
tp_price = None
sl_price = None

preload_history()
start_polling()

while True:
    try:
        df = get_ohlcv_df()
        print(df.tail(3))
        if len(df) < 20:
            print("Waiting for enough candles...")
            time.sleep(1)
            continue

        df = calculate_bollinger_bands(df)
        signal = generate_bollinger_signal(df)
        price = df['close'].iloc[-1]

        print(f"Last Close: {price:.2f} | Signal: {signal} | Position: {position}")

        if position is None:
            if signal == 'buy':
                place_order('buy')
                log_trade(f"{signal.upper()} | Price: {price} | Position: {position}")

                position = 'long'
                entry_price = price
                tp_price, sl_price = calculate_tp_sl(entry_price, position)
                send_alert(f"🟢 Entered LONG at {price:.2f} | TP: {tp_price}, SL: {sl_price}")

            elif signal == 'sell':
                place_order('sell')
                log_trade(f"{signal.upper()} | Price: {price} | Position: {position}")

                position = 'short'
                entry_price = price
                tp_price, sl_price = calculate_tp_sl(entry_price, position)
                send_alert(f"🔴 Entered SHORT at {price:.2f} | TP: {tp_price}, SL: {sl_price}")

        else:
            # Check for manual exit
            if (position == 'long' and signal == 'exit_long') or (position == 'short' and signal == 'exit_short'):
                place_order(signal)
                log_trade(f"{signal.upper()} | Price: {price} | Position: {position}")

                send_alert(f"↩️ Manual exit from {position.upper()} at {price:.2f}")
                position = None

            # Check for TP or SL
            elif should_exit(position, price, tp_price, sl_price):
                exit_signal = 'exit_long' if position == 'long' else 'exit_short'
                place_order(exit_signal)
                log_trade(f"{exit_signal.upper()} | Price: {price} | Position: {position}")

                send_alert(f"🏁 {position.upper()} EXIT triggered at {price:.2f} (TP/SL hit)")
                position = None

        time.sleep(2)  # faster cycle for mock testing

    except Exception as e:
        print("⚠️ Error:", e)
        time.sleep(5)
