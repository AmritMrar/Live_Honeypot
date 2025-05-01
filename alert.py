import requests

BOT_TOKEN = "7739240201:AAFjgJ2O984S1dmH1JScMYSlZICJwsmqWRs"
CHAT_ID = "1312121239"

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send alert: {e}")
