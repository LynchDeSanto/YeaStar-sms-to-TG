import socket
import urllib.parse
from config import YEASTAR_ADDRESS, YEASTAR_PORT, API_USER, API_PASSWORD

def decode_sms(raw_content: str) -> str:
    """Decoding SMS message"""
    return urllib.parse.unquote(raw_content).replace("+", " ")

def listen_sms_api(callback):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((YEASTAR_ADDRESS, YEASTAR_PORT))
    login_payload = f"Action: Login\r\nUsername: {API_USER}\r\nSecret: {API_PASSWORD}\r\n\r\n"
    s.sendall(login_payload.encode("utf-8"))

    # Начальные ответы
    s.recv(1024)
    s.recv(1024)

    print("[+] Подключено к Yeastar API. Ожидание новых SMS...")

    while True:
        try:
            data = s.recv(4096).decode("utf-8")
            if "Event: ReceivedSMS" in data:
                lines = data.split("\r\n")
                sms_info = {line.split(": ")[0]: line.split(": ")[1] for line in lines if ": " in line}
                gsm_port = sms_info.get("GsmSpan")
                sender = sms_info.get("Sender")
                content = decode_sms(sms_info.get("Content", ""))
                recvtime = sms_info.get("Recvtime")
                callback(sender, gsm_port, content, recvtime)
        except Exception as e:
            print(f"[!] Ошибка чтения SMS: {e}")
            break
