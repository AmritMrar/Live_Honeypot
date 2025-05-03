import socket
import threading
import requests
import datetime

# Telegram Bot details
BOT_TOKEN = "7739240201:AAFjgJ2O984S1dmH1JScMYSlZICJwsmqWRs"
CHAT_ID = "1312121239"

# Log file paths
LOG_FILE = "port_logs.txt"
TELEGRAM_LOG_FILE = "telegram_alerts.txt"

# Fake service banners
BANNERS = {
    2222: "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.3\r\n",
    3306: "5.7.26-log MySQL Community Server (GPL)\r\n",
    8081: "HTTP/1.1 200 OK\r\nServer: Apache\r\n\r\n",
    9001: "Welcome to Secure Portal v1.0\r\n",
}

# Ports to monitor
PORTS_TO_WATCH = [2222, 3306, 8081, 9001]

def log_event(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}\n"
    with open(LOG_FILE, "a") as f:
        f.write(log_line)
    print("📝", log_line.strip())

def log_telegram_alert(message):
    with open(TELEGRAM_LOG_FILE, "a") as f:
        f.write(message + "\n")

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=data)
        if response.ok:
            print("✅ Telegram alert sent.")
            log_telegram_alert(message)
        else:
            print("❌ Telegram failed:", response.text)
            log_event(f"Telegram Error: {response.text}")
    except Exception as e:
        print("❌ Telegram Exception:", e)
        log_event(f"Telegram Exception: {e}")

def handle_connection(port, client_socket, client_address):
    ip, src_port = client_address
    log_msg = f"[+] Connection from {ip}:{src_port} on port {port}"
    log_event(log_msg)

    try:
        data = client_socket.recv(1024)
        if data:
            log_event(f"📥 Data received from {ip}:{port} - {data.decode(errors='ignore')}")
    except:
        pass

    try:
        banner = BANNERS.get(port, "Unauthorized access detected.\r\n")
        client_socket.sendall(banner.encode())
    except Exception as e:
        log_event(f"Error sending banner: {e}")

    alert = (
        f"⚠️ Port Scan Detected!\n"
        f"🖥️ IP: {ip}\n"
        f"🔌 Source Port: {src_port}\n"
        f"🎯 Target Port: {port}\n"
        f"🕒 Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    send_telegram_alert(alert)

    client_socket.close()

def run_port_honeypot(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(1.0)  # Enables scan responsiveness
        sock.bind(("0.0.0.0", port))
        sock.listen(5)
        log_event(f"🛡️ Listening on port {port}")
    except Exception as e:
        log_event(f"❌ Failed to bind port {port}: {e}")
        return

    while True:
        try:
            client_socket, client_address = sock.accept()
            thread = threading.Thread(target=handle_connection, args=(port, client_socket, client_address))
            thread.start()
        except socket.timeout:
            continue
        except Exception as e:
            log_event(f"Socket error on port {port}: {e}")

def start_port_honeypots():
    for port in PORTS_TO_WATCH:
        thread = threading.Thread(target=run_port_honeypot, args=(port,))
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    log_event("🚀 Port-based Honeypot Started")
    start_port_honeypots()

    # Keep the main thread alive
    try:
        while True:
            pass
    except KeyboardInterrupt:
        log_event("🛑 Honeypot terminated by user")
