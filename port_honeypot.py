import socket
import threading
import datetime
import requests

# ✅ Telegram Config
BOT_TOKEN = "7739240201:AAFjgJ2O984S1dmH1JScMYSlZICJwsmqWRs"
CHAT_ID = "1312121239"

# ✅ Config
PORTS_TO_WATCH = [3306, 8081]
LOG_FILE = "port_logs.txt"
FLASK_LOG_ENDPOINT = "http://localhost:5000/api/logs"

# ✅ Fake service banners (realistic)
FAKE_BANNERS = {
    3306: b"\x00\x00\x00\x0a5.7.31-0ubuntu0.18.04.1\x00\x00\x00\x00\x00\x00\x00\x00mysql_native_password\x00",
    8081: b"HTTP/1.1 200 OK\r\nServer: Apache\r\nContent-Type: text/html\r\n\r\n<h1>Fake Admin Panel</h1>"
}

def log_event(message):
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    full_message = f"{timestamp} {message}"
    print(full_message)

    # Write to file
    with open(LOG_FILE, "a") as f:
        f.write(full_message + "\n")

    # Push to Flask API
    try:
        requests.post(FLASK_LOG_ENDPOINT, json={"log": full_message})
    except Exception as e:
        print(f"[!] Flask push failed: {e}")

def send_telegram_alert(ip, port):
    msg = f"⚠️ Port Scan Detected\nIP: {ip}\nPort: {port}\nTime: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
        if response.ok:
            print("✅ Telegram alert sent.")
        else:
            log_event(f"[!] Telegram failed: {response.text}")
    except Exception as e:
        log_event(f"[!] Telegram error: {e}")

def handle_connection(client_socket, client_address, port):
    ip = client_address[0]
    log_event(f"🚨 Connection on port {port} from {ip}")
    send_telegram_alert(ip, port)

    try:
        banner = FAKE_BANNERS.get(port, b"\n")
        client_socket.sendall(banner)
    except Exception as e:
        log_event(f"[!] Error sending banner on port {port}: {e}")
    finally:
        client_socket.close()

def listen_on_port(port):
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", port))
        server.listen(5)
        log_event(f"🛡️ Listening on port {port}")
    except Exception as e:
        log_event(f"❌ Failed to bind port {port}: {e}")
        return

    while True:
        try:
            client_socket, client_address = server.accept()
            threading.Thread(
                target=handle_connection,
                args=(client_socket, client_address, port),
                daemon=True
            ).start()
        except Exception as e:
            log_event(f"[!] Socket error on port {port}: {e}")

def start_honeypots():
    log_event("🚀 Port-based Honeypot Started")
    for port in PORTS_TO_WATCH:
        threading.Thread(target=listen_on_port, args=(port,), daemon=True).start()

if __name__ == "__main__":
    start_honeypots()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        log_event("🛑 Honeypot terminated by user")
