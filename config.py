import os
from dotenv import load_dotenv

load_dotenv()

# Yeastar API
YEASTAR_ADDRESS = os.getenv("YEASTAR_ADDRESS")
YEASTAR_PORT = int(os.getenv("YEASTAR_PORT", 5038))
API_USER = os.getenv("API_USER")
API_PASSWORD = os.getenv("API_PASSWORD")

# Telegram
TG_TOKEN = os.getenv("TG_TOKEN")
TG_CHAT = os.getenv("TG_CHAT")

# Логи
LOG_FOLDER = "logs"
import os
os.makedirs(LOG_FOLDER, exist_ok=True)

# Словарь GsmSpan → номер SIM (для идентификации порта)
PORT_SIM_MAP = {
    "2": "+78005553535",
}
