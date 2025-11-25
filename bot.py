from telegram_bot import run_telegram_bot
from sms_api import listen_sms_api
from config import TG_TOKEN, LOG_FOLDER, PORT_SIM_MAP

def sms_callback(sender, gsm_port, content, recvtime):
    sim_number = PORT_SIM_MAP.get(gsm_port, f"Port {gsm_port}")
    log_file = f"{LOG_FOLDER}/sms_{gsm_port}.txt"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{recvtime}] От: {sender} на SIM {sim_number}\n{content}\n\n")
    print(f"[SMS] От: {sender}, Порт: {gsm_port}, Текст: {content}")

if __name__ == "__main__":
    import threading
    # Запускаем слушателя SMS в отдельном потоке
    threading.Thread(target=listen_sms_api, args=(sms_callback,), daemon=True).start()
    # Запускаем Telegram-бота
    run_telegram_bot(TG_TOKEN)
