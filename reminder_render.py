import os
import requests
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

app = Flask(__name__)

def auto_ping():
    requests.get("https://your-render-url.onrender.com/")

@app.route("/")
def home():
    return "Lucy reminder bot is running!"

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    message = "🔔 Mọi người ơi nhớ điền kết quả công việc ngày hôm qua vào sheet tiến độ, và cuối ngày nhớ báo cáo bitrix nhé!"
    await context.bot.send_message(chat_id=CHAT_ID, text=message)

async def handle_mention(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.entities:
        for entity in update.message.entities:
            if entity.type == "mention":
                bot_username = (await context.bot.get_me()).username
                mention_text = update.message.text[entity.offset: entity.offset + entity.length]
                if mention_text == f"@{bot_username}":
                    await update.message.reply_text("Lucy đã ghi nhận, anh cần hỗ trợ gì thêm không?")
                    break

if __name__ == "__main__":
    app_scheduler = BackgroundScheduler()
    app_scheduler.add_job(auto_ping, "interval", minutes=5)
    app_scheduler.start()

    bot_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    bot_app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_mention))

    bot_app.job_queue.run_daily(
        send_reminder,
        time=datetime.strptime("17:15", "%H:%M").time(),
        days=(0, 1, 2, 3, 4, 5)
    )

    import threading
    threading.Thread(target=bot_app.run_polling, daemon=True).start()
    app.run(host="0.0.0.0", port=8080)
