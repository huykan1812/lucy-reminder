from datetime import datetime
from flask import Flask
import threading
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
REMINDER_TEXT = "⏰ Mọi người ơi cập nhật tiến độ công việc lên sheet kế hoạch, và cuối ngày nhớ báo cáo Bitrix nhé!"
INTERVAL_SECONDS = 300  # 5 phút

app = Flask(__name__)

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Lỗi khi gửi tin nhắn: {e}")

def reminder_loop():
    while True:
        now = datetime.now()
        if now.hour == 8 and now.minute == 30:
            send_telegram_message(REMINDER_TEXT)
            time.sleep(60)
        time.sleep(10)

@app.route('/')
def home():
    return "Lucy reminder bot đang hoạt động!"

def keep_alive():
    app.run(host='0.0.0.0', port=8080)

flask_thread = threading.Thread(target=keep_alive)
flask_thread.daemon = True
flask_thread.start()

reminder_loop()
