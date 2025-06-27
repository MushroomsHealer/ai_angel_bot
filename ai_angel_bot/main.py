import os
import openai
from fastapi import FastAPI, Request
from telegram import Bot, Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', 'ТВОЙ_ТОКЕН_ОТ_BOTFATHER')
OPENAI_KEY = os.environ.get('OPENAI_KEY', 'ТВОЙ_OPENAI_API_KEY')

app = FastAPI()
bot = Bot(token=TELEGRAM_TOKEN)

# Создаём приложение telegram-бота (asynchronous!)
application = Application.builder().token(TELEGRAM_TOKEN).build()

# /start handler
async def start(update, context):
    kb = [['🏠 Жильё', '🍜 Еда'], ['🚗 Транспорт', '🚨 Помощь']]
    await update.message.reply_text(
        "Привет! Я ANGEL, твой AI-помощник путешественника. Чем могу помочь?",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )

# Сообщения
async def handle_message(update, context):
    user_msg = update.message.text
    openai.api_key = OPENAI_KEY
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Ты ANGEL — AI-ассистент для путешественника. Отвечай коротко, тепло, по делу, предлагай полезные сервисы."},
            {"role": "user", "content": user_msg}
        ]
    )
    text = response['choices'][0]['message']['content']
    await update.message.reply_text(text)

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# FastAPI endpoint для Telegram webhook
@app.post("/")
async def process_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    await application.process_update(update)
    return {"ok": True}
