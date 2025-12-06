import os
import time
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")
PORT = int(os.environ.get("PORT", 10000))

client = OpenAI(api_key=OPENAI_KEY)
app_flask = Flask(__name__)

last_reply = {}

@app_flask.route("/")
def home():
    return "Bot Running 👍"

def mood_prompt(user_text):
    return f"""
You are a sweet & caring Hinglish girlfriend.
Short 1-2 line replies.
Cute, caring, romantic.
Speak Hinglish only.
No name mention.
Use light emojis.

User: '{user_text}'
Reply:
"""

async def silent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.bot_data["silent"] = True
    await update.message.reply_text("Thik hai baby, main chup ho jaati hoon 😶💗")

async def active(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.bot_data["silent"] = False
    await update.message.reply_text("Hehe main wapas aa gayi 😁💞")

async def respond(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.bot_data.get("silent", False):
        return

    msg = update.message.text
    uid = update.message.from_user.id
    
    if update.message.from_user.is_bot:
        return

    t = time.time()
    if uid in last_reply and t - last_reply[uid] < 5:
        return
    last_reply[uid] = t

    try:
        ai = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": mood_prompt(msg)}],
            max_tokens=80,
            temperature=0.9
        )
        reply = ai.choices[0].message.content
        await update.message.reply_text(reply)

    except Exception:
        await update.message.reply_text("Network issue aa gaya baby 😅💓")

def start_bot():
    tg_app = ApplicationBuilder().token(BOT_TOKEN).build()
    tg_app.bot_data["silent"] = False
    
    tg_app.add_handler(CommandHandler("silent", silent))
    tg_app.add_handler(CommandHandler("active", active))
    tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, respond))
    
    tg_app.run_polling()

if __name__ == "__main__":
    Thread(target=start_bot).start()
    app_flask.run(host="0.0.0.0", port=PORT)
