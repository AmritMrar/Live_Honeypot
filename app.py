from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import logging
import requests
from datetime import datetime

app = Flask(__name__)

# Telegram Bot Credentials
BOT_TOKEN = "7739240201:AAFjgJ2O984S1dmH1JScMYSlZICJwsmqWRs"
CHAT_ID = "1312121239"

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
web_log_handler = logging.FileHandler('web_logs.txt')
web_log_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(web_log_handler)

# Telegram Alert Function
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=payload)
        print("Telegram status:", response.status_code, response.text)
    except Exception as e:
        logging.error(f"Telegram Error: {e}")

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        suspicious_keywords = ['<script>', 'SELECT', 'DROP', '1=1', '--', '#', 'OR', 'AND', "' OR '1'='1"]

        if any(keyword.lower() in email.lower() or keyword.lower() in password.lower() for keyword in suspicious_keywords):
            log_entry = f"[{datetime.now()}] Suspicious input detected - Email: {email}, Password: {password}\n"
            with open("web_logs.txt", "a") as web_log:
                web_log.write(log_entry)
            alert_msg = f"⚠️ Web Honeypot Alert\nEmail: {email}\nPassword: {password}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            send_telegram_alert(alert_msg)

        if email == 'test@example.com' and password == 'password123':
            return redirect(url_for('index'))
        else:
            return "Invalid credentials, please try again."
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/get_logs')
def get_logs():
    web_logs = ""
    port_logs = ""
    if os.path.exists("web_logs.txt"):
        with open("web_logs.txt", "r") as web_log:
            web_logs = web_log.read()
    if os.path.exists("port_logs.txt"):
        with open("port_logs.txt", "r") as port_log:
            port_logs = port_log.read()
    return jsonify({"web_logs": web_logs, "port_logs": port_logs})

if __name__ == '__main__':
    app.run(debug=True)
