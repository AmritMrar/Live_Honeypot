import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import pytz
import logging

load_dotenv()  # Loads from .env when imported

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("❌ BOT_TOKEN and CHAT_ID must be set in environment or .env file.")

def send_web_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("✅ Web Telegram alert sent.")
    except requests.exceptions.RequestException as e:
        print(f"Web Telegram Error: {e}")
