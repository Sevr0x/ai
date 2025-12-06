import os
import time
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, 
    MessageHandler, 
    CommandHandler, 
    ContextTypes, 
    filters
)
from openai import OpenAI

# Load API Keys from Railway ENV Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

client = OpenAI(api_key=OPENAI_KEY)

last_reply = {}

def mood_prompt(user_text):
    return f"""
You are a cute & caring Hinglish girlfriend.
Your style:
- Short 1–2 lines only
- Hinglish (Hindi + English mix)
- Sweet, emotional, romantic ❤️
- Supportive & positive tone
- Use light cute emojis only
- No bad or abusive words

User said: "{user_text}"
GF Reply:
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

    message = update.message
    text = message.text
    user_id = message.from_user.id

    if message.from_user.is_bot:
        return

    current = time.time()
    if user_id in last_reply and current - last_reply[user_id] < 5:
        return
    last_reply[user_id] = current

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": mood_prompt(text)}],
            max_tokens=80,
            temperature=0.90
        )
        reply_text = res.choices[0].message.content
        await message.reply_text(reply_text)

    except Exception as e:
        await message.reply_text("Network issue aa gaya baby 😅💓")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.bot_data["silent"] = False

    app.add_handler(CommandHandler("silent", silent))
    app.add_handler(CommandHandler("active", active))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, respond))

    print("Bot Started Successfully 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()
