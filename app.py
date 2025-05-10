from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import logging
from datetime import datetime
import pytz
from alert import send_alert  # Import from alert.py

app = Flask(__name__)

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
        ip = request.remote_addr
        timestamp = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')

        if any(kw.lower() in email.lower() or kw.lower() in password.lower() for kw in suspicious_keywords):
            log_msg = f"[{timestamp}] Suspicious input - IP: {ip}, Email: {email}, Password: {password}"
            logger.info(log_msg)
            send_alert(f"⚠️ Web Honeypot Alert\nIP: {ip}\nEmail: {email}\nPassword: {password}\nTime: {timestamp}")

        if email == 'test@example.com' and password == 'password123':
            return redirect(url_for('index'))

        return "Invalid credentials, please try again."
    return render_template('login.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    ip = request.remote_addr
    timestamp = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')

    if any(kw.lower() in query.lower() for kw in suspicious_keywords):
        log_msg = f"[{timestamp}] Suspicious search input - IP: {ip}, Query: {query}"
        logger.info(log_msg)
        send_alert(f"⚠️ Web Honeypot Alert\nSuspicious Search Input: {query}\nIP: {ip}\nTime: {timestamp}")

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
    send_alert("🚨 Test alert from live honeypot!")
    return "Test Telegram alert sent."

@app.route('/favicon.ico')
def favicon():
    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)), debug=False)
