import os
import logging
from flask import Flask, request, redirect, url_for, render_template
from datetime import datetime
import pytz
import requests

app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

print(f"Bot Token: {BOT_TOKEN}")
print(f"Chat ID: {CHAT_ID}")

logging.basicConfig(filename='web_logs.txt', level=logging.INFO)

def send_telegram_alert(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message}
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Telegram Error: {e}")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        suspicious_keywords = ["admin", "root", "sql", "drop", "select", "delete", "insert", "passwd"]

        if any(keyword.lower() in email.lower() or keyword.lower() in password.lower() for keyword in suspicious_keywords):
            log_entry = f"[{datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')}] Suspicious input detected - Email: {email}, Password: {password}\n"
            with open("web_logs.txt", "a") as web_log:
                web_log.write(log_entry)
            alert_msg = f"⚠️ Web Honeypot Alert\nEmail: {email}\nPassword: {password}\nTime: {datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')}"
            send_telegram_alert(alert_msg)

        if email == 'test@example.com' and password == 'password123':
            return redirect(url_for('index'))
        else:
            return "Invalid credentials, please try again."
    return render_template('login.html')

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    try:
        with open("web_logs.txt", "r") as f:
            logs = f.readlines()
    except FileNotFoundError:
        logs = []
    return render_template("dashboard.html", logs=logs)

if __name__ == "__main__":
    print("Bot Token:", BOT_TOKEN)
    print("Chat ID:", CHAT_ID)
    app.run(host="0.0.0.0", port=5001, debug=False)
