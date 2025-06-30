import os, json, threading
from flask import Flask, request
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ---------- Configuration ----------
BOT_TOKEN = os.getenv("BOT_TOKEN")            # set in Railway → Variables
USER_FILE = "gf_id.json"                      # where we store her ID
bot       = telegram.Bot(token=BOT_TOKEN)

# ---------- Helpers ----------
def save_user_id(uid: int):
    with open(USER_FILE, "w") as f:
        json.dump({"gf_id": uid}, f)

def load_user_id():
    if not os.path.exists(USER_FILE):
        return None
    with open(USER_FILE) as f:
        return json.load(f).get("gf_id")

# ---------- Telegram part ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    save_user_id(uid)
    await update.message.reply_text(
        "Hi love 💖 I'm ready to send you letters anytime!"
    )
    print(f"✅ Saved user ID: {uid}")

telegram_app = Application.builder().token(BOT_TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))

def run_telegram():
    telegram_app.run_polling()

# ---------- Flask part ----------
flask_app = Flask(__name__)

@flask_app.route("/sendletter")
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
          "lost": "Even when you feel lost, I’ll help you find your way 🧭",
          "default": "Hi baby 💖 I’m always here."
    }
    msg  = mood_messages.get(mood, mood_messages["default"])
    uid  = load_user_id()
    if uid:
        bot.send_message(chat_id=uid, text=msg)
        return "Message sent 💌"
    return "No user ID yet — ask her to /start the bot first."

# ---------- Main ----------
if __name__ == "__main__":
    # 1️⃣ start Telegram bot in a background thread
    threading.Thread(target=run_telegram, daemon=True).start()
    # 2️⃣ run Flask web server (Railway will map PORT env var)
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))