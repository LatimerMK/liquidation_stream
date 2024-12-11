# ========================== стрфм + фільтр ліквідацій
import websocket
import json
from datetime import datetime

def liquidationOrder(size, ignor_list):
    print(f"Size: {size} $ \nIgnore: {ignor_list}")
    def forceOrder_msg(_wsa, data):
        parsed_data = json.loads(data)
        #print(parsed_data)

        if parsed_data['o']['s'] not in ignor_list:
            val = float(parsed_data['o']['p']) * float(parsed_data['o']['q'])

            if val > size:
                timestamp = datetime.fromtimestamp(parsed_data['E'] / 1000.0)
                timeLiq = timestamp.strftime("%H:%M:%S")
                if parsed_data['o']['S'] == "BUY":
                    side = "Liqd SHORT 🔴  "
                else: side = "Liqd LONG  🟢  "

                formatted_val = "{:,.2f}".format(val)
                formatted_symbol = parsed_data['o']['s']
                if len(parsed_data['o']['s']) < 15:
                    formatted_symbol += (' ' * (15-len(parsed_data['o']['s'])))

                print(f"{timeLiq}   -   {formatted_symbol}  {side}  {formatted_val} $ https://www.coinglass.com/tv/Binance_{parsed_data['o']['s']}")


        if parsed_data['o']['s'] in ignor_list:
            val = float(parsed_data['o']['p']) * float(parsed_data['o']['q'])

            if val > size * 10:
                timestamp = datetime.fromtimestamp(parsed_data['E'] / 1000.0)
                timeLiq = timestamp.strftime("%H:%M:%S")
                if parsed_data['o']['S'] == "BUY":
                    side = "Liqd SHORT 🔴🔴"
                else:
                    side = "Liqd LONG  🟢🟢"

                formatted_val = "{:,.2f}".format(val)
                formatted_symbol = parsed_data['o']['s']
                if len(parsed_data['o']['s']) < 15:
                    formatted_symbol += (' ' * (15-len(parsed_data['o']['s'])))
                print(
                    f"{timeLiq}  >>>  {formatted_symbol}  {side}  {formatted_val} $ https://www.coinglass.com/tv/Binance_{parsed_data['o']['s']}")

    def forceOrder():

        print("start liquidation stream")
        stream_name = "!forceOrder@arr"
        wss = "wss://fstream.binance.com/ws/%s" % stream_name
        wsa = websocket.WebSocketApp(wss, on_message=forceOrder_msg)
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

# Приклад використання
liquidationOrder(size=liquidation_order_params["size"], ignor_list=top_25_coin)
