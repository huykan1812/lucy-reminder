import os
import threading
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)
from openai import OpenAI
from apscheduler.schedulers.background import BackgroundScheduler

# Load biến môi trường
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Flask để giữ bot online (autoping)
app = Flask(__name__)
@app.route('/')
def home():
    return "Lucy bot is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# Tự động nhắn tin mỗi sáng 8h30 từ thứ 2 đến thứ 7
async def send_daily_reminder(application):
    now = datetime.now().strftime("%H:%M %d/%m/%Y")
    text = f"📢 [{now}] Mọi người ơi nhớ điền kết quả công việc ngày hôm qua vào sheet tiến độ, và cuối ngày nhớ báo cáo bitrix nhé!"
    await application.bot.send_message(chat_id=CHAT_ID, text=text)

# Trả lời khi được @mention
async def handle_mention(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    bot_username = context.bot.username

    if update.message.chat.type != "private" and f"@{bot_username}" not in text:
        return  # Không phản hồi nếu không được mention

    user_id = str(update.effective_user.id)
    messages = [
        {"role": "system", "content": "Bạn là Lucy, một Trợ Lý cá nhân chuyên hỗ trợ báo cáo công việc, xưng Em với người dùng là Anh."},
        {"role": "user", "content": text}
    ]
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"Lỗi: {e}"
    await update.message.reply_text(reply)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    app_bot = ApplicationBuilder().token(TOKEN).build()

    # Handler: chỉ trả lời khi được @mention
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_mention))

    # Scheduler: nhắc mỗi sáng 8h30 từ T2 đến T7
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_daily_reminder, "cron", day_of_week="mon-sat", hour=17, minute=15, args=[app_bot])
    scheduler.start()

    print("✅ Lucy bot đang hoạt động với nhắc việc + mention filter!")
    app_bot.run_polling()
