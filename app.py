from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import logging
import requests
from datetime import datetime
import pytz

app = Flask(__name__)

# Telegram Bot Credentials
BOT_TOKEN = os.getenv("BOT_TOKEN", "7739240201:AAFjgJ2O984S1dmH1JScMYSlZICJwsmqWRs")
CHAT_ID = os.getenv("CHAT_ID", "1312121239")

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
        logger.error(f"Telegram Error: {e}")

# Suspicious keyword list
suspicious_keywords = [
    '<script>', 'SELECT', 'DROP', '1=1', '--', '#', 'OR', 'AND', "' OR '1'='1'",
    'INSERT', 'UPDATE', 'DELETE', 'MERGE', 'EXEC', 'UNION', 'ALTER', 'CREATE',
    'TABLE', 'DATABASE', 'TRUNCATE', 'GRANT', 'REVOKE', 'VALUES', 'WHERE', 'HAVING',
    'JOIN', 'ORDER BY', 'GROUP BY', 'LIMIT', 'OFFSET', "' OR 'x'='x'", "' AND '1'='1'",
    "' AND 'x'='x'", ';', '/*', '*/', 'xp_cmdshell', 'sp_executesql',
    'CAST(', 'CONVERT(', 'DECLARE', '@@version', '@@hostname',
    'alert(', 'document.cookie', 'window.location', 'onmouseover=', 'onerror=',
    'eval(', 'setTimeout(', 'setInterval(', 'console.log(', 'fetch(', 'XMLHttpRequest(',
    'innerHTML=', 'outerHTML=', 'javascript:', 'iframe', 'src=', 'data:text/html;base64,',
    '<img src=x onerror=alert(1)>', 'passwd', 'etc/passwd', '/etc/shadow', '.htaccess',
    '/bin/bash', 'cmd.exe', 'powershell', '$(', '||', '|&', 'wget', 'curl',
    'python -c', 'perl -e', 'ruby -e', 'php://input', 'file://', '../', '..\\',
    '%00', '%0A', '%0D', '%3C', '%3E', 'sleep(', 'benchmark(', 'load_file(',
    'outfile', 'dumpfile', 'hex(', 'base64_decode(', 'base64_encode(', 'concat(', 'substr('
]

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if any(kw.lower() in email.lower() or kw.lower() in password.lower() for kw in suspicious_keywords):
            timestamp = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
            log_msg = f"[{timestamp}] Suspicious input - Email: {email}, Password: {password}"
            logger.info(log_msg)
            send_telegram_alert(f"⚠️ Web Honeypot Alert\nEmail: {email}\nPassword: {password}\nTime: {timestamp}")
        if email == 'test@example.com' and password == 'password123':
            return redirect(url_for('index'))
        return "Invalid credentials, please try again."
    return render_template('login.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    if any(kw.lower() in query.lower() for kw in suspicious_keywords):
        timestamp = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] Suspicious search input: {query}"
        logger.info(log_msg)
        send_telegram_alert(f"⚠️ Web Honeypot Alert\nSuspicious Search Input: {query}\nTime: {timestamp}")
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/get_logs')
def get_logs():
    web_logs = ""
    port_logs = ""
    if os.path.exists("web_logs.txt"):
        with open("web_logs.txt", "r") as f:
            web_logs = f.read()
    if os.path.exists("port_logs.txt"):
        with open("port_logs.txt", "r") as f:
            port_logs = f.read()
    return jsonify({"web_logs": web_logs, "port_logs": port_logs})

@app.route('/api/logs', methods=['POST'])
def receive_log():
    data = request.get_json()
    log_line = data.get("log", "")
    if log_line:
        with open("port_logs.txt", "a") as f:
            f.write(log_line + "\n")
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
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)), debug=False)
