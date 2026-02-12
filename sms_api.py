from collections import defaultdict
from threading import Lock
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

# Multipart buffer
sms_buffer = {}
buffer_lock = Lock()
MULTIPART_TTL = 300  # 5 минут

def log_raw(data: str):
    with open(RAW_LOG, "a", encoding="utf-8") as f:
        f.write(data + "\n")


def handle_sms_event(event_text: str):
    lines = event_text.splitlines()
    data = {}

    for line in lines:
        if ":" in line:
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip()

    if data.get("Event") != "ReceivedSMS":
        return

    sender = data.get("Sender", "Unknown")
    gsm_span = data.get("GsmSpan", "Unknown")
    msg_ref = data.get("MsgRef")
    index = data.get("Index")
    total = data.get("Total")

    raw_content = data.get("Content", "")
    text = unquote_plus(raw_content).lstrip("\ufeff") if raw_content else ""

    sim_number = PORT_SIM_MAP.get(gsm_span, f"GsmSpan {gsm_span}")

    # --- Multipart handling ---
    if msg_ref and index and total:
        try:
            index = int(index)
            total = int(total)
        except ValueError:
            return

        key = (sender, msg_ref, gsm_span)

        with buffer_lock:
            # cleanup old messages
            now = time.time()
            expired_keys = [
                k for k, v in sms_buffer.items()
                if now - v["timestamp"] > MULTIPART_TTL
            ]
            for k in expired_keys:
                del sms_buffer[k]

            if key not in sms_buffer:
                sms_buffer[key] = {
                    "total": total,
                    "parts": {},
                    "timestamp": now,
                    "gsm_span": gsm_span
                }

            sms_buffer[key]["parts"][index] = text

            # if all parts received
            if len(sms_buffer[key]["parts"]) == total:
                full_text = "".join(
                    sms_buffer[key]["parts"][i]
                    for i in sorted(sms_buffer[key]["parts"])
                )

                print(f"[SMS] Multipart complete from {sender}: {full_text}")

                send_sms_to_telegram(sender, sim_number, full_text)

                del sms_buffer[key]

        return

    # --- Single part SMS ---
    if text:
        print(f"[SMS] Single SMS from {sender}: {text}")
        send_sms_to_telegram(sender, sim_number, text)


def listen_sms_api():
    while True:
        try:
            print("[INFO] Connecting to Yeastar API...")

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(300)  # увеличили timeout
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
                try:
                    chunk = sock.recv(4096)
                except socket.timeout:
                    continue  # просто ждём дальше

                if not chunk:
                    raise ConnectionError("AMI disconnected")

                decoded = chunk.decode("utf-8", errors="ignore")
                buffer += decoded
                log_raw(decoded)

                while "--END SMS EVENT--" in buffer:
                    event, buffer = buffer.split("--END SMS EVENT--", 1)
                    handle_sms_event(event.strip())

        except KeyboardInterrupt:
            print("[INFO] Stopped by user.")
            break

        except Exception as e:
            print(f"[ERROR] {e}")
            print("[INFO] Reconnect in 5 seconds...")
            time.sleep(5)
