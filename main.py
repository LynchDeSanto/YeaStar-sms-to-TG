import socket
import urllib.parse
import requests
import datetime
import os
from dotenv import load_dotenv

# ================== НАСТРОЙКИ ==================
load_dotenv()

ADDRESS = os.getenv("YEASTAR_ADDRESS")
PORT = 5038
USER = os.getenv("API_USER")
PASSWORD = os.getenv("API_PASSWORD")

TELEGRAM_TOKEN = os.getenv("TG_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TG_CHAT")

LOG_FOLDER = "logs"
os.makedirs(LOG_FOLDER, exist_ok=True)

# Словарь GsmSpan → номер SIM
PORT_SIM_MAP = {
    "2": "+78005553535",
}
# ================================================

def decode_sms(text):
    decoded = urllib.parse.unquote_plus(text)
    if decoded.startswith("\ufeff"):
        decoded = decoded.replace("\ufeff", "", 1)
    return decoded

def log_sms(message):
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(LOG_FOLDER, f"sms_{now}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(message + "\n")

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=5)
    except Exception as e:
        print("[!] Ошибка отправки в Telegram:", e)

def parse_sms_event(event_text):
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
