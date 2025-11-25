import asyncio
from telegram import Bot
from config import TG_TOKEN, TG_CHAT

bot = Bot(token=TG_TOKEN)

def send_to_telegram(message: str):
    try:
        asyncio.run(bot.send_message(chat_id=TG_CHAT, text=message))
    except Exception as e:
        print(f"[!] Ошибка отправки в Telegram: {e}")
