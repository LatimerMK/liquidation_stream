# binance_api.py
import pandas as pd
import os
from dotenv import load_dotenv
from binance.um_futures import UMFutures

load_dotenv()
API_KEY = os.getenv("API_KEY_BINANCE")
API_SECRET = os.getenv("API_SECRET_BINANCE")

client = UMFutures(key=API_KEY, secret=API_SECRET)
print("[Binance API] Client initialized.")


def get_klines(symbol: str, interval: str = "15m", limit: int = 200):
    print(f"[Binance API] Fetching {limit} klines for {symbol} on {interval} interval...")
    klines = client.klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    print(f"[Binance API] Retrieved data shape: {df.shape}")
    return df


def get_channel_levels(df):
    """
    Calculate the channel levels (high/low) based on the data frame.
    This function finds the highest and lowest points within the given data.
    """
    # For simplicity, we're calculating the max and min of the 'high' and 'low' prices in the given timeframe.
    high_level = df['high'].max()
    low_level = df['low'].min()

    print(f"[Channel Levels] Highest level: {high_level}")
    print(f"[Channel Levels] Lowest level: {low_level}")

    return high_level, low_level


def test_active_assets(symbols: list):
    print("[Test] Monitoring the following assets:", symbols)
    for symbol in symbols:
        print(f"[Test] Analyzing {symbol}...")
        df = get_klines(symbol)
        # Calculate channel levels
        high_level, low_level = get_channel_levels(df)
        # Here you can implement further checks, like detecting channels, checking for conditions
        print(f"[Test] Data for {symbol} retrieved. Data sample:\n{df.head()}")
        # Example placeholder for channel detection
        print(f"[Test] Checking for channel in {symbol}...")
        # Here you could analyze the channel using custom logic
        print(f"[Test] Channel analysis complete for {symbol}.")
