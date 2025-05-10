# alert.py

import os
import requests
import logging
from datetime import datetime
import pytz

# Environment variables (with defaults)
BOT_TOKEN = os.getenv("BOT_TOKEN", "7739240201:AAFjgJ2O984S1dmH1JScMYSlZICJwsmqWRs")
CHAT_ID = os.getenv("CHAT_ID", "1312121239")

# Setup logging with IST
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

def send_alert(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message}
        response = requests.post(url, data=payload)
        response.raise_for_status()
        logger.info("✅ Telegram alert sent.")
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Telegram alert failed: {e}")

# Manual test
if __name__ == "__main__":
    send_alert("🚨 This is a test alert from alert.py.")
