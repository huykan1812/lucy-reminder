
import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from datetime import datetime
import requests
from dotenv import load_dotenv
from apscheduler.executors.pool import ThreadPoolExecutor

load_dotenv()

# Cài đặt bot token và group chat ID
TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")
AUTO_PING_URL = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8080")

# Tạo bot application
app_bot = ApplicationBuilder().token(TOKEN).build()
scheduler = BackgroundScheduler()
flask_app = Flask(__name__)

# Hàm gửi tin nhắn nhắc nhở hằng ngày lúc 17:15 (trừ Chủ Nhật)
async def daily_reminder(context: CallbackContext):
    if datetime.now().weekday() != 6:
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text="Mọi người ơi nhớ điền kết quả công việc ngày hôm qua vào sheet tiến độ, và cuối ngày nhớ báo cáo bitrix nhé"
        )

# Tạo job queue sau khi ứng dụng khởi tạo
async def on_startup(app):
    app.job_queue.run_daily(
        callback=daily_reminder,
        time=datetime.strptime("17:15", "%H:%M").time(),
        days=(0, 1, 2, 3, 4, 5)
    )

# Chỉ phản hồi tin nhắn có mention bot
async def handle_mentions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and context.bot.username in update.message.text:
        await update.message.reply_text("Lucy đã nhận được lời gọi!")

# Đăng ký handler và khởi tạo job queue
app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_mentions))
app_bot.post_init = on_startup

# Flask route cho autoping
@flask_app.route("/")
def home():
    return "Lucy reminder bot is live!"

@flask_app.route("/ping")
def ping():
    return "pong"

# Hàm autoping
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

# Chạy song song bot và Flask server
if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: flask_app.run(host="0.0.0.0", port=8080)).start()
    app_bot.run_polling()
