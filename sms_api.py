import socket
import time
import os
from urllib.parse import unquote_plus
from datetime import datetime

from config import (
    YEASTAR_ADDRESS,
    YEASTAR_PORT,
    API_USER,
    API_PASSWORD,
    PORT_SIM_MAP,
    LOG_DIR,
)
from bot import send_sms_to_telegram

os.makedirs(LOG_DIR, exist_ok=True)
RAW_LOG = os.path.join(LOG_DIR, "ami_raw.log")


def log_raw(data: str):
    with open(RAW_LOG, "a", encoding="utf-8") as f:
        f.write(data + "\n")


def handle_sms_event(event_text: str):
    lines = event_text.splitlines()
    data = {k.strip(): v.strip() for line in lines if ":" in line for k,v in [line.split(":",1)]}

    for line in lines:
        if ":" in line:
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip()

    if data.get("Event") != "ReceivedSMS":
        return

    sender = data.get("Sender", "Unknown")
    gsm_span = data.get("GsmSpan", "Unknown")
    raw_content = data.get("Content", "")
    text = unquote_plus(raw_content).lstrip("\ufeff") if raw_content else "(пустое сообщение)"
    sim_number = PORT_SIM_MAP.get(gsm_span, f"GsmSpan {gsm_span}")

    print(f"[SMS] От: {sender}, SIM: {sim_number}, Текст: {text}")
    send_sms_to_telegram(sender, sim_number, text)


def listen_sms_api():
    while True:
        try:
            print("[INFO] Connecting to Yeastar API...")

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(60)
            sock.connect((YEASTAR_ADDRESS, YEASTAR_PORT))

            login_payload = (
                f"Action: Login\r\n"
                f"Username: {API_USER}\r\n"
                f"Secret: {API_PASSWORD}\r\n\r\n"
            )
            sock.sendall(login_payload.encode())

            print("[INFO] Connected. Waiting for SMS...")

            buffer = ""

            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    raise ConnectionError("AMI disconnected")

                decoded = chunk.decode("utf-8", errors="ignore")
                buffer += decoded
                log_raw(decoded)

                while "--END SMS EVENT--" in buffer:
                    event, buffer = buffer.split("--END SMS EVENT--", 1)
                    handle_sms_event(event.strip())

        except Exception as e:
            print(f"[ERROR] {e}")
            print("[INFO] Reconnect in 5 seconds...")
            time.sleep(5)