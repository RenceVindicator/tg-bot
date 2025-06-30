from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

TOKEN = os.getenv("BOT_TOKEN")   # Railway will inject this

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mood = context.args[0] if context.args else "default"

    replies = {
        "sad":    "Hey love 😢— sending you virtual hugs 💖",
        "happy":  "Woo‑hoo! Your joy is my joy 😄",
        "tired":  "Rest now, I’m proud of you 💤",
        "lost":   "I’m right here with you 🧭",
        "default":"Hi babe! I’m always a message away 💌"
    }
    await update.message.reply_text(replies.get(mood, replies["default"]))

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()