def generate_bollinger_signal(df):
    """
    Generates signal based on last candle.
    Returns: 'buy', 'sell', 'exit', or None
    """
    if len(df) < 2:
        return None

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # Entry signals
    if last['close'] > last['upper_band'] and prev['close'] <= prev['upper_band']:
        return 'sell'
    elif last['close'] < last['lower_band'] and prev['close'] >= prev['lower_band']:
        return 'buy'

    # Exit signals (return to SMA)
    elif prev['close'] < prev['sma'] and last['close'] >= last['sma']:
        return 'exit_long'
    elif prev['close'] > prev['sma'] and last['close'] <= last['sma']:
        return 'exit_short'

    return None
