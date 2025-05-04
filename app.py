from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import logging
import requests
from datetime import datetime
import pytz

app = Flask(__name__)

# ✅ Telegram Bot Credentials (hardcoded for now)
BOT_TOKEN = '7739240201:AAFjgJ2O984S1dmH1JScMYSlZICJwsmqWRs'
CHAT_ID = '1312121239'

# Setup logging with IST timezone
class ISTFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ist = pytz.timezone('Asia/Kolkata')
        dt = datetime.fromtimestamp(record.created, tz=ist)
        return dt.strftime(datefmt or "%Y-%m-%d %H:%M:%S")

formatter = ISTFormatter("[%(asctime)s] %(message)s")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
for handler in logger.handlers:
    handler.setFormatter(formatter)

# File log handler
web_log_handler = logging.FileHandler('web_logs.txt')
web_log_handler.setLevel(logging.INFO)
web_log_handler.setFormatter(formatter)
logger.addHandler(web_log_handler)

# Telegram Alert Function
def send_telegram_alert(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message}
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
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
        suspicious_keywords = [...]  # (same long list as before — keep it as-is)

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

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    suspicious_keywords = [...]  # (same long list as before — keep it as-is)

    if any(keyword.lower() in query.lower() for keyword in suspicious_keywords):
        log_entry = f"[{datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')}] Suspicious search input: {query}\n"
        with open("web_logs.txt", "a") as web_log:
            web_log.write(log_entry)
        alert_msg = f"⚠️ Web Honeypot Alert\nSuspicious Search Input: {query}\nTime: {datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')}"
        send_telegram_alert(alert_msg)

    return redirect(url_for('index'))

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

@app.route('/api/logs', methods=['POST'])
def receive_log():
    data = request.get_json()
    log_line = data.get("log", "")
    if log_line:
        with open("port_logs.txt", "a") as port_log:
            port_log.write(log_line + "\n")
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "no log received"}), 400

@app.route('/test-telegram')
def test_telegram():
    send_telegram_alert("🚨 Test alert from live honeypot!")
    return "Test Telegram alert sent."

@app.route('/favicon.ico')
def favicon():
    return '', 200

if __name__ == '__main__':
    print("Bot Token:", BOT_TOKEN)
    print("Chat ID:", CHAT_ID)
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5050)), debug=False)
