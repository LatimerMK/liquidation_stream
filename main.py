# ========================== стрфм + фільтр ліквідацій
import websocket
import json
from datetime import datetime
import requests
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from collections import deque
from binance_api import get_klines
from chart_create import find_significant_levels, plot_candlestick_with_levels
from alert_manager import send_alert

# Завантажити змінні з .env
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
# Зберігає кортежі (timestamp, value)
liquidation_history = deque()


def format_sum(val):
    if val >= 1_000_000_000:
        return f"{val / 1_000_000_000:.2f}kkk"
    elif val >= 1_000_000:
        return f"{val / 1_000_000:.2f}kk"
    elif val >= 100_000:
        return f"{val / 1_000:.0f}k"
    elif val >= 10_000:
        return f"{val / 1_000:.0f}k"
    elif val >= 1_000:
        return f"{val / 1_000:.0f}k"
    else:
        return f"{val:.0f}"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'Markdown'
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"❌ Error sending message to Telegram: {e}")

import threading
import time

message_buffer = []
buffer_lock = threading.Lock()
SEND_INTERVAL = 5  # Кожні 5 секунд
MAX_MESSAGE_LENGTH = 4000  # Безпечна межа, трохи нижче 4096

def buffer_worker():
    while True:
        time.sleep(SEND_INTERVAL)
        with buffer_lock:
            if message_buffer:
                # Об'єднуємо всі повідомлення
                combined_msg = "\n".join(message_buffer)
                message_buffer.clear()

                # Якщо довше за ліміт — розбити
                for i in range(0, len(combined_msg), MAX_MESSAGE_LENGTH):
                    chunk = combined_msg[i:i+MAX_MESSAGE_LENGTH]
                    send_telegram_message(chunk)

# Запустити окремий потік
threading.Thread(target=buffer_worker, daemon=True).start()

def add_to_buffer(text):
    with buffer_lock:
        message_buffer.append(text)



def liquidationOrder(size, ignor_list):

    msg1=f"Size: {size} $ \nIgnore: {ignor_list}"
    print(msg1)
    #send_telegram_message(msg1)
    def forceOrder_msg(_wsa, data):
        parsed_data = json.loads(data)
        #print(parsed_data)

        val = float(parsed_data['o']['p']) * float(parsed_data['o']['q'])
        now = datetime.utcnow()
        # Додаємо нову ліквідацію
        liquidation_history.append((now, val))
        # Видаляємо старі записи старші за 1 годину
        one_hour_ago = now - timedelta(hours=1)
        while liquidation_history and liquidation_history[0][0] < one_hour_ago:
            liquidation_history.popleft()
        # Рахуємо суму за останню годину
        hourly_sum = sum(v for t, v in liquidation_history)
        #print(f"Сума ліквідацій за останню годину: {hourly_sum:,.0f} $")
        symbol = parsed_data['o']['s']
        INTERVAL = "5m"
        LIMIT = 500
        chart_path = f"charts/{symbol}.png"

        if parsed_data['o']['s'] not in ignor_list:


            if val > size:
                timestamp = datetime.fromtimestamp(parsed_data['E'] / 1000.0)
                timeLiq = timestamp.strftime("%H:%M:%S")
                if parsed_data['o']['S'] == "BUY":
                    side = "Liqd 🔴"
                else: side = "Liqd 🟢"

                formatted_val = "{:,.0f}".format(val)
                formatted_symbol = parsed_data['o']['s']
                if len(parsed_data['o']['s']) < 15:
                    formatted_symbol += (' ' * (15-len(parsed_data['o']['s'])))

                print(f"{timeLiq}   -   {formatted_symbol}  {side}  {formatted_val} $ https://www.coinglass.com/tv/Binance_{parsed_data['o']['s']}  🚀 All 1H: {format_sum(hourly_sum)} $")
                msg = (f"[{formatted_symbol}](https://www.coinglass.com/tv/Binance_{parsed_data['o']['s']})  {side}  {formatted_val} $  🚀 All 1H: {format_sum(hourly_sum)} $")
                #add_to_buffer(msg)
                ###########################################################################
                msg = {
                    "link": f"<a href='https://www.coinglass.com/tv/Binance_{parsed_data['o']['s']}'>{formatted_symbol} </a>",
                    # f"[{color}{symbol}](https://www.coinglass.com/tv/Binance_{symbol})",
                    "liqd_val": f"{side}  {formatted_val} $ ",
                    "all_liqd": f"🚀 All 1H: {format_sum(hourly_sum)} $"
                }


                df = get_klines(f"{symbol}", interval=INTERVAL, limit=LIMIT)
                # current_price = df.iloc[-1]['close']
                if len(df) < LIMIT * 0.5:
                    return
                levels, alines = find_significant_levels(df, order=25, min_diff_percent=1, max_crossings=2,
                                                         lookback=5, )

                plot_candlestick_with_levels(df, symbol, interval=INTERVAL, save_path=chart_path, alines=alines)
                send_alert(symbol, msg, chart_path)


        if parsed_data['o']['s'] in ignor_list:

            if val > size * 10:
                timestamp = datetime.fromtimestamp(parsed_data['E'] / 1000.0)
                timeLiq = timestamp.strftime("%H:%M:%S")
                if parsed_data['o']['S'] == "BUY":
                    side = "Liqd 🔴🔴"
                else:
                    side = "Liqd 🟢🟢"

                formatted_val = "{:,.0f}".format(val)
                formatted_symbol = parsed_data['o']['s']
                if len(parsed_data['o']['s']) < 15:
                    formatted_symbol += (' ' * (15-len(parsed_data['o']['s'])))
                print( f"{timeLiq}  >>>  {formatted_symbol}  {side}  {formatted_val} $ https://www.coinglass.com/tv/Binance_{parsed_data['o']['s']}  🚀 All 1H: {format_sum(hourly_sum)} $")
                msg = (f"[{formatted_symbol}](https://www.coinglass.com/tv/Binance_{parsed_data['o']['s']})  {side}  {formatted_val} $  🚀 All 1H: {format_sum(hourly_sum)} $")
                #add_to_buffer(msg)
                ###########################################################################
                msg = {
                    "link": f"<a href='https://www.coinglass.com/tv/Binance_{parsed_data['o']['s']}'>{formatted_symbol} </a>",
                    # f"[{color}{symbol}](https://www.coinglass.com/tv/Binance_{symbol})",
                    "liqd_val": f"{side} {formatted_val} $ ",
                    "all_liqd": f"🚀 All 1H: {format_sum(hourly_sum)} $"
                }

                df = get_klines(f"{symbol}", interval=INTERVAL, limit=LIMIT)
                # current_price = df.iloc[-1]['close']
                if len(df) < LIMIT * 0.5:
                    return
                levels, alines = find_significant_levels(df, order=25, min_diff_percent=1, max_crossings=2,
                                                         lookback=5, )

                plot_candlestick_with_levels(df, symbol, interval=INTERVAL, save_path=chart_path, alines=alines)
                send_alert(symbol, msg, chart_path)


    def forceOrder():

        print("start liquidation stream")
        stream_name = "!forceOrder@arr"
        wss = "wss://fstream.binance.com/ws/%s" % stream_name
        wsa = websocket.WebSocketApp(wss, on_message=forceOrder_msg)
        #websocket.enableTrace(True)
        wsa.run_forever()

    forceOrder()
# -------------------------------------------------------------------
# Завантаження конфігурації з файлу
with open("config.json", "r") as file:
    config = json.load(file)

# Використання параметрів
top_25_coin = config["top_25_coin"]
top_10_coin = config["top_10_coin"]
liquidation_order_params = config["liquidation_order"]
send_telegram_message(f"Start Bot - Liquidation Stream")
# Приклад використання
liquidationOrder(size=liquidation_order_params["size"], ignor_list=top_25_coin)
