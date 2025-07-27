import pandas as pd

def calculate_bollinger_bands(df, period=20, stddev=2):
    df['ma'] = df['close'].rolling(window=period).mean()
    df['std'] = df['close'].rolling(window=period).std()
    df['upper'] = df['ma'] + stddev * df['std']
    df['lower'] = df['ma'] - stddev * df['std']
    return df

def generate_bollinger_signal(df):
    if len(df) < 20:
        return None

    close = df['close'].iloc[-1]
    upper = df['upper'].iloc[-1]
    lower = df['lower'].iloc[-1]

    # Signal logic
    if close < lower:
        return 'buy'
    elif close > upper:
        return 'sell'
    else:
        return None
