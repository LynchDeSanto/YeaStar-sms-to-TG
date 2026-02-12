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

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Dictionary GsmSpan → SIM number
PORT_SIM_MAP = {}
for key, value in os.environ.items():
    if key.startswith("PORT_SIM_MAP_"):
        port = key.replace("PORT_SIM_MAP_", "")
        PORT_SIM_MAP[port] = value

print(PORT_SIM_MAP)
