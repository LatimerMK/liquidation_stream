# alert_manager.py
from telegram_bot import send_telegram_message, send_telegram_photo


def send_alert(symbol: str, msg: str, chart_path: str = None):
    message = format_channel_alert(symbol, msg)

    if chart_path:
        send_telegram_photo(chart_path, caption=message)
    else:
        send_telegram_message(message)


def format_channel_alert(symbol: str, msg: dict) -> str:

    alert = f"<b>{msg['link']}</b> "
    alert += f"{msg['liqd_val']} "
    alert += f"{msg['all_liqd']} "


    return alert.strip()

