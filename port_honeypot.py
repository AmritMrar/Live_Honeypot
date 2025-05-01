import socket
import threading
import requests
import datetime

# Telegram Bot details
BOT_TOKEN = "7739240201:AAFjgJ2O984S1dmH1JScMYSlZICJwsmqWRs"
CHAT_ID = "1312121239"

# Log file path
LOG_FILE = "port_logs.txt"

# Fake service banners
BANNERS = {
    22: "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.3\r\n",
    3306: "5.7.26-log MySQL Community Server (GPL)\r\n",
    8081: "HTTP/1.1 200 OK\r\nServer: Apache\r\n\r\n",
    9001: "Welcome to Secure Portal v1.0\r\n",
}

# Log events to file and print to console
def log_event(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}\n"
    with open(LOG_FILE, "a") as f:
        f.write(log_line)
        f.flush()
    print("📝", log_line.strip())

# Send Telegram alert
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=data)
        if response.ok:
            print("✅ Telegram alert sent.")
        else:
            print("❌ Telegram failed:", response.text)
            log_event(f"Telegram Error: {response.text}")
    except Exception as e:
        print("❌ Telegram Exception:", e)
        log_event(f"Telegram Exception: {e}")

# Handle incoming connection
def handle_connection(port, client_socket, client_address):
    ip = client_address[0]
    log_msg = f"Connection from {ip} on port {port}"
    print("🔌", log_msg)
    log_event(log_msg)
    send_telegram_alert(f"⚠️ Port Honeypot Alert!\nIP: {ip}\nPort: {port}")

    try:
        banner = BANNERS.get(port, "Unauthorized access detected.\r\n")
        client_socket.sendall(banner.encode())
    except Exception as e:
        log_event(f"Error sending banner: {e}")

    client_socket.close()

# Start honeypot on a specific port
def run_port_honeypot(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        sock.bind(("0.0.0.0", port))
        sock.listen(5)
        print(f"🛡️ Port Honeypot listening on port {port}")
        log_event(f"Listening on port {port}")
    except Exception as e:
        log_event(f"Failed to bind port {port}: {e}")
        return

    while True:
        client_socket, client_address = sock.accept()
        thread = threading.Thread(target=handle_connection, args=(port, client_socket, client_address))
        thread.start()

# Start honeypots on multiple ports
def start_port_honeypots():
    ports_to_watch = [22, 3306, 8081, 9001]
    for port in ports_to_watch:
        thread = threading.Thread(target=run_port_honeypot, args=(port,))
        thread.start()

# Run the honeypot system
if __name__ == "__main__":
    start_port_honeypots()
