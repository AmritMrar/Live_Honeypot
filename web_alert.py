# web_alert.py

import os
import requests
import logging
from datetime import datetime
import pytz
from dotenv import load_dotenv

# Load .env variables
load_dotenv(dotenv_path=".env.web")

# Web Honeypot Telegram Credentials
WEB_BOT_TOKEN = os.getenv("WEB_BOT_TOKEN")
WEB_CHAT_ID = os.getenv("WEB_CHAT_ID")

if not WEB_BOT_TOKEN or not WEB_CHAT_ID:
    raise ValueError("❌ WEB_BOT_TOKEN and WEB_CHAT_ID must be set as environment variables.")

# Logging setup with IST timezone
class ISTFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ist = pytz.timezone('Asia/Kolkata')
        dt = datetime.fromtimestamp(record.created, tz=ist)
        return dt.strftime(datefmt or "%Y-%m-%d %H:%M:%S")

formatter = ISTFormatter("[%(asctime)s] %(message)s")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("web_alert")
for handler in logger.handlers:
    handler.setFormatter(formatter)

logger.info(f"[DEBUG] Using TOKEN: {WEB_BOT_TOKEN}")
logger.info(f"[DEBUG] Using CHAT_ID: {WEB_CHAT_ID}")


def send_web_alert(message):
    url = f"https://api.telegram.org/bot{WEB_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": WEB_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        logger.info("✅ Web Telegram alert sent.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Telegram Error: {e}")
