import os
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

app = Flask(__name__)

@app.route('/')
def home():
    return "Lucy reminder bot is alive!"

def send_reminder():
    text = "📬 Chào buổi sáng mọi người! Nhớ cập nhật số lượng lên sheet kế hoạch và cuối ngày nhớ báo cáo Bitrix nhé 💼"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    try:
        response = requests.post(url, data=data)
        print(f"[{response.status_code}] Nhắc việc đã gửi lúc 8h30 sáng.")
    except Exception as e:
        print(f"❌ Lỗi gửi nhắc việc: {e}")

# Lên lịch nhắc mỗi 8h30 sáng
scheduler = BackgroundScheduler()
scheduler.add_job(send_reminder, 'cron', hour=8, minute=30)
scheduler.start()

if __name__ == "__main__":
    print("🕒 Lucy reminder bot đã khởi động!")
    app.run(host="0.0.0.0", port=8080)