import matplotlib.pyplot as plt
import numpy as np


from binance_api import get_klines
import pandas as pd
from scipy.signal import argrelextrema
import mplfinance as mpf


def round_level(value, base=100):
    return int(base * round(float(value) / base))


def find_significant_levels(df, order=10, min_diff_percent=1, max_crossings=2, lookback=5,):
    df = df.copy()
    levels = []

    local_max_idx = argrelextrema(df['high'].values, np.greater, order=order)[0]
    local_min_idx = argrelextrema(df['low'].values, np.less, order=order)[0]
    #all_indices = np.sort(np.concatenate((local_max_idx, local_min_idx)))

    for idx in local_max_idx:
        level = df['high'].iloc[idx]
        levels.append((idx, level))

    for idx in local_min_idx:
        level = df['low'].iloc[idx]
        levels.append((idx, level))

    # Фільтрація близьких рівнів за допомогою відсотків
    filtered = []
    for idx, lvl in levels:
        # Якщо це перший рівень, то додаємо його
        if not filtered:
            filtered.append((idx, lvl))
        else:
            # Порівнюємо відсоткову різницю між поточним рівнем і попередніми
            prev_idx, prev_lvl = filtered[-1]
            price_diff_percent = abs(lvl - prev_lvl) / prev_lvl * 100

            # Якщо відсоткова різниця більша або рівна заданому мінімуму, додаємо рівень
            if price_diff_percent >= min_diff_percent:
                filtered.append((idx, lvl))

    levels = filtered
    ################################
    df = df.copy()
    df.columns = [c.capitalize() for c in df.columns]  # Open, High, Low, Close, Volume
    alines = []
    updated_levels = []
    for idx, lvl in levels:
        crossings = 0
        last_cross_idx = -lookback
        points = []
        broke = False  # прапорець для виявлення break

        for i in range(idx + 1, len(df)):
            prev_price = df['Close'].iloc[i - 1]
            curr_price = df['Close'].iloc[i]

            if (curr_price >= lvl > prev_price) or (curr_price <= lvl < prev_price):
                if i - last_cross_idx >= lookback:
                    crossings += 1
                    last_cross_idx = i

            if crossings >= max_crossings:
                broke = True
                break

            points.append((df.index[i], lvl))
        updated_levels.append((idx, lvl, crossings))  # додаємо crossings

        if not broke and len(points) >= 2:

            alines.append(points)
    ##############################
    return updated_levels, alines



def plot_candlestick_with_levels(df, symbol, interval, alines, save_path: str = "charts.png"):
    df = df.copy()
    df.columns = [c.capitalize() for c in df.columns]  # Open, High, Low, Close, Volume
    #alines = []
    # Додаємо 10 пустих рядків з тими ж стовпцями
    n_padding = int(len(df) * 0.1)
    last_time = df.index[-1]
    freq = df.index.inferred_freq or '1min'  # якщо не знайдено частоти, ставимо 1 хв

    # Видаляємо стовпці з усіма NA значеннями з df
    df = df.dropna(axis=1, how='all')
    # Генеруємо майбутні дати
    future_dates = pd.date_range(start=last_time, periods=n_padding + 1, freq=freq)[1:]
    # Створюємо пустий DataFrame з тими ж колонками
    empty_data = pd.DataFrame(index=future_dates, columns=df.columns)
    # Видаляємо стовпці з усіма NA значеннями з empty_data (якщо такі є)
    empty_data = empty_data.dropna(axis=1, how='all')
    # Тепер виконуємо конкатенацію з пустими даними
    df_extended = pd.concat([df, empty_data], axis=0)

    style = mpf.make_mpf_style(
        base_mpf_style="nightclouds",
        rc={
            'axes.labelsize': 8,
            'axes.titlesize': 10,
            'xtick.labelsize': 7,
            'ytick.labelsize': 7,
        },
        facecolor='#111111', edgecolor='#111111', gridcolor='#444444',
        gridstyle=':', mavcolors=['#00ff00', '#ff0000']
    )

    # Побудова графіка (без linestyles)
    mpf.plot(
        df_extended,
        type='candle',
        style=style,
        alines=dict(alines=alines, colors=['green'] * len(alines), alpha=0.5, linewidths=[1] * len(alines)),
        ylabel='Price',
        volume=True,
        title=f'{symbol} - {interval}',  # ← Додано заголовок
        figsize=(14, 6),
        tight_layout=True,
        savefig=dict(fname=save_path, dpi=300, bbox_inches='tight')
    )


if __name__ == '__main__':
    symbol = "SUIUSDT"
    chart_path = f"charts/{symbol}.png"

    df = get_klines(f"{symbol}", interval="30m", limit=500)

    levels, alines = find_significant_levels(df, order=25, min_diff_percent=1, max_crossings=2, lookback=5,)
    print(alines)

    plot_candlestick_with_levels(df, save_path=chart_path, alines=alines)

