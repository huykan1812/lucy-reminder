import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, ContextTypes, MessageHandler,
    filters, CallbackContext, Application
)
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from flask import Flask
from datetime import datetime
import requests
from dotenv import load_dotenv
import threading

load_dotenv()

# Cấu hình
TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")
AUTO_PING_URL = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8080")

# Flask app
flask_app = Flask(__name__)

# Bot Application
app_bot = ApplicationBuilder().token(TOKEN).post_init(lambda app: app.job_queue.run_daily(
    callback=daily_reminder,
    time=datetime.strptime("17:15", "%H:%M").time(),
    days=(0, 1, 2, 3, 4, 5),  # Thứ 2 -> Thứ 7
)).build()

# Hàm nhắc việc mỗi chiều
async def daily_reminder(context: CallbackContext):
    if datetime.now().weekday() != 6:
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text="Mọi người ơi nhớ điền kết quả công việc ngày hôm nay vào sheet tiến độ, và cuối ngày nhớ báo cáo bitrix nhé"
        )

# Chỉ trả lời nếu bot được mention
async def handle_mentions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and context.bot.username in update.message.text:
        await update.message.reply_text("Lucy đã nhận được lời gọi!")

# Đăng ký handler
app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_mentions))

# Flask route
@flask_app.route("/")
def home():
    return "Lucy reminder bot is live!"

@flask_app.route("/ping")
def ping():
    return "pong"

# Autoping
def auto_ping():
    try:
        requests.get(AUTO_PING_URL)
    except Exception as e:
        logging.error(f"Autoping failed: {e}")

executors = {
    'default': ThreadPoolExecutor(max_workers=10)
}
scheduler = BackgroundScheduler(executors=executors, timezone="Asia/Ho_Chi_Minh")
scheduler.add_job(auto_ping, "interval", minutes=5)
scheduler.start()

# Chạy Flask và bot song song
if __name__ == "__main__":
    threading.Thread(target=lambda: flask_app.run(host="0.0.0.0", port=8080)).start()
    app_bot.run_polling()
