import requests
from config import TG_TOKEN, TG_CHAT

def send_sms_to_telegram(sender: str, sim: str, text: str):
    message = (
        "📩 Новая SMS\n"
        f"От: {sender}\n"
        f"На SIM: {sim}\n"
        f"Текст: {text}"
    )

    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT,
        "text": message
    }

    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Telegram send failed: {e}")

