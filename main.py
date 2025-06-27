import os
import openai
from fastapi import FastAPI, Request
from telegram import Bot, Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TELEGRAM_TOKEN = os.environ.get('8153785782:AAHutXmNmen_U6OW_aPLB1fo-lvcLynZLtU')
OPENAI_KEY = os.environ.get('OPENAI_KEY')

app = FastAPI()
bot = Bot(token=TELEGRAM_TOKEN)

application = Application.builder().token(TELEGRAM_TOKEN).build()
app_inited = False  # Глобальный флаг инициализации

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [['🏠 Жильё', '🍜 Еда'], ['🚗 Транспорт', '🚨 Помощь']]
    await update.message.reply_text(
        "Привет! Я ANGEL, твой AI-помощник путешественника. Чем могу помочь?",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )

# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    openai.api_key = OPENAI_KEY
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Ты ANGEL — AI-ассистент для путешественника. Отвечай коротко, тепло, по делу, предлагай полезные сервисы."},
                {"role": "user", "content": user_msg}
            ]
        )
        text = response['choices'][0]['message']['content']
    except Exception as e:
        text = f"Ошибка OpenAI: {e}"
    await update.message.reply_text(text)

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Endpoint для Telegram Webhook
@app.post("/")
async def process_webhook(request: Request):
    global app_inited
    data = await request.json()
    update = Update.de_json(data, bot)
    # Инициализация application (обязательно!)
    if not app_inited:
        await application.initialize()
        app_inited = True
    await application.process_update(update)
    return {"ok": True}
