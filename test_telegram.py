import requests
import os
from dotenv import load_dotenv

load_dotenv()  # ✅ This makes sure .env is loaded when run as script or imported

BOT_TOKEN = os.getenv("BOT_TOKEN", "7739240201:AAFjgJ2O984S1dmH1JScMYSlZICJwsmqWRs")
CHAT_ID = os.getenv("CHAT_ID", "1312121239")
MESSAGE = "✅ Test message from Honeypot Bot"

def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, data=data)
    return response.json()

if __name__ == "__main__":
    result = send_telegram_message(BOT_TOKEN, CHAT_ID, MESSAGE)
    print("Telegram Response:", result)
