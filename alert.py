# alert.py

import os
import requests
import logging
from datetime import datetime
import pytz

# ✅ Don't allow fallback to default values
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("❌ BOT_TOKEN and CHAT_ID must be set as environment variables.")

def send_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("✅ Telegram alert sent.")
    except requests.exceptions.RequestException as e:
        print(f"Telegram Error: {e}")
        
# Logging setup with IST timezone
class ISTFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ist = pytz.timezone('Asia/Kolkata')
        dt = datetime.fromtimestamp(record.created, tz=ist)
        return dt.strftime(datefmt or "%Y-%m-%d %H:%M:%S")

formatter = ISTFormatter("[%(asctime)s] %(message)s")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("alert")
for handler in logger.handlers:
    handler.setFormatter(formatter)


