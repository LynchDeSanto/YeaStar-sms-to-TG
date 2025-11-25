from sms_api import listen_sms_api
from bot import send_to_telegram
from config import LOG_FOLDER, PORT_SIM_MAP

def sms_callback(sender, gsm_port, content, recvtime):
    sim_number = PORT_SIM_MAP.get(gsm_port, f"Port {gsm_port}")
    log_file = f"{LOG_FOLDER}/sms_{gsm_port}.txt"

    telegram_message = f"📩 Новая SMS\nОт: {sender}\nНа SIM: {sim_number}\nТекст: {content}"

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{recvtime}] {telegram_message}\n\n")

    send_to_telegram(telegram_message)

    print(f"[SMS] От: {sender}, Порт: {gsm_port}, Текст: {content}")

if __name__ == "__main__":
    listen_sms_api(sms_callback)
