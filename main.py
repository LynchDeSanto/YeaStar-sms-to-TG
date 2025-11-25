import socket
import urllib.parse
import requests
import datetime
import os

# ================== НАСТРОЙКИ ==================
ADDRESS = os.getenv("AMI_ADDRESS")
PORT = int(os.getenv("AMI_PORT"))
USER = os.getenv("AMI_USER")
PASSWORD = os.getenv("AMI_PASSWORD")

TELEGRAM_TOKEN = os.getenv("TG_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TG_CHAT")

# Папка для логов
LOG_FOLDER = "logs"
os.makedirs(LOG_FOLDER, exist_ok=True)

# Словарь соответствия GsmSpan и номера SIM
PORT_SIM_MAP = {
    "GsmSpan-number": "Phone_number",  # GsmSpan 2 → номер твоей SIM
    # Добавляй новые порты при необходимости
}
# ================================================

def decode_sms(text):
    """Декодирует URL-encoded UTF-8 SMS и убирает BOM, если есть"""
    decoded = urllib.parse.unquote_plus(text)
    if decoded.startswith("\ufeff"):
        decoded = decoded.replace("\ufeff", "", 1)
    return decoded

def log_sms(message):
    """Сохраняет SMS в лог-файл"""
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(LOG_FOLDER, f"sms_{now}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(message + "\n")

def send_to_telegram(text):
    """Отправка текста в Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=5)
    except Exception as e:
        print("[!] Ошибка отправки в Telegram:", e)

def parse_sms_event(event_text):
    """Разбор блока события ReceivedSMS"""
    sender = ""
    port = ""
    content_raw = ""

    for line in event_text.splitlines():
        if line.startswith("Sender:"):
            sender = line.split(":", 1)[1].strip()
        if line.startswith("GsmSpan:"):
            port = line.split(":", 1)[1].strip()
        if line.startswith("Content:"):
            content_raw = line.split(":", 1)[1].strip()

    if content_raw:
        content = decode_sms(content_raw)
        sim_number = PORT_SIM_MAP.get(port, f"Неизвестный порт ({port})")
        message = f"📩 Новая SMS\nОт: {sender}\nНа SIM: {sim_number}\nТекст: {content}"
        print(message)
        send_to_telegram(message)
        log_sms(message)

def listen_sms_ami():
    """Основной цикл прослушки AMI"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ADDRESS, PORT))
    banner = s.recv(1024).decode(errors="ignore")
    print("[+] Подключено к AMI:", banner.strip())

    login = (
        f"Action: Login\r\n"
        f"Username: {USER}\r\n"
        f"Secret: {PASSWORD}\r\n"
        f"Events: on\r\n\r\n"
    )
    s.send(login.encode())
    response = s.recv(1024).decode(errors="ignore")
    print("[+] Ответ авторизации:", response.strip())

    if "Success" not in response:
        print("[!] Авторизация не удалась!")
        return

    print("[✅] Авторизация успешна. Ждём SMS...\n")
    buffer = ""

    while True:
        try:
            data = s.recv(4096).decode(errors="ignore")
            if not data:
                continue
            buffer += data
            while "--END SMS EVENT--" in buffer:
                event_block, buffer = buffer.split("--END SMS EVENT--", 1)
                if "Event: ReceivedSMS" in event_block:
                    parse_sms_event(event_block)
        except Exception as e:
            print("[!] Ошибка:", e)
            break

if __name__ == "__main__":
    listen_sms_ami()
