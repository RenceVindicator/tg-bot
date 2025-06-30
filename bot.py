from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

TOKEN = os.getenv("BOT_TOKEN")   # Railway will inject this

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mood = context.args[0] if context.args else "default"

responses = {
    "sad": "I'm here for you, love 😢💗",
    "happy": "You're glowing! Keep smiling 😄✨",
    "mad": "Take a deep breath, I’m here no matter what 😤❤️",
    "tired": "Rest, my love. You deserve it 💤",
    "stress": "I'm hugging you through the stress 🤗💆‍♀️",
    "excited": "Yay! Tell me everything! 🎉💕",
    "proud": "So proud of you 😭💖",
    "lost": "Even when you feel lost, I’ll help you find your way 🧭"
}
    await update.message.reply_text(responses.get(mood, replies["default"]))

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()