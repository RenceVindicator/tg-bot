import os
import json
import threading
from flask import Flask, request
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telegram.Bot(token=BOT_TOKEN)

# File to store the user ID
USER_FILE = "gf_id.json"

# Save user ID to file
def save_user_id(user_id):
    with open(USER_FILE, "w") as f:
        json.dump({"gf_id": user_id}, f)

# Load user ID from file
def load_user_id():
    if not os.path.exists(USER_FILE):
        return None
    with open(USER_FILE, "r") as f:
        return json.load(f).get("gf_id")

# ----------- Flask App for Sending Letter -------------
app = Flask(__name__)

@app.route('/sendletter')
def send_letter():
    mood = request.args.get("mood", "default")
    mood_messages = {
    "sad": "I'm here for you, love 😢💗",
    "happy": "You're glowing! Keep smiling 😄✨",
    "mad": "Take a deep breath, I’m here no matter what 😤❤️",
    "tired": "Rest, my love. You deserve it 💤",
    "stress": "I'm hugging you through the stress 🤗💆‍♀️",
    "excited": "Yay! Tell me everything! 🎉💕",
    "proud": "So proud of you 😭💖",
    "lost": "Even when you feel lost, I’ll help you find your way 🧭"
    "default": "Hi baby 💖 I’m always here."
    }
    message = mood_messages.get(mood, mood_messages["default"])

    gf_id = load_user_id()
    if gf_id:
        bot.send_message(chat_id=gf_id, text=message)
        return "Message sent to your love 💌"
    else:
        return "No user ID saved yet. Ask her to send /start first."

# ----------- Telegram Bot Part -------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user_id(user_id)
    await update.message.reply_text("Hi love 💖 I'm ready to send you letters anytime!")
    print(f"✅ Saved user ID: {user_id}")

def run_telegram_bot():
    app_telegram = Application.builder().token(BOT_TOKEN).build()
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.run_polling()

# ----------- Main Entrypoint -------------
if __name__ == "__main__":
    threading.Thread(target=run_telegram_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
