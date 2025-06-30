from flask import Flask, request, abort
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os, json, asyncio

# === Config from Railway ENV variables ===
BOT_TOKEN      = os.getenv("BOT_TOKEN")
APP_URL        = os.getenv("APP_URL")  # e.g. https://your-app.up.railway.app
WEBHOOK_PATH   = os.getenv("WEBHOOK_PATH", "telegram")
USER_FILE      = "gf_id.json"

# === Init Telegram and Flask ===
bot = Bot(token=BOT_TOKEN)
tg_app = Application.builder().token(BOT_TOKEN).build()
app = Flask(__name__)

# === Save / load user ID ===
def save_uid(uid: int):
    with open(USER_FILE, "w") as f:
        json.dump({"gf_id": uid}, f)

def load_uid():
    if not os.path.exists(USER_FILE):
        return None
    with open(USER_FILE) as f:
        return json.load(f).get("gf_id")

# === /start handler ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    save_uid(uid)
    await update.message.reply_text("Hi love 💖 I'm ready to send you letters anytime!")
    print(f"✅ Saved user ID: {uid}")

tg_app.add_handler(CommandHandler("start", start))

# === Telegram Webhook Endpoint ===
@app.post(f"/{WEBHOOK_PATH}")
async def telegram_webhook():
    if request.headers.get("content-type") != "application/json":
        return abort(415)
    update = Update.de_json(request.get_json(force=True), bot)
    await tg_app.process_update(update)
    return "OK"

# === /sendletter route ===
@app.get("/sendletter")
def send_letter():
    mood = request.args.get("mood", "default")
    messages = {
        "sad":    "I'm here for you, love 😢💗",
        "tired":  "Rest well, you deserve all the love in the world 💌",
        "happy":  "You're glowing 🌟 and I love it!",
        "mad":    "Whatever it is, I’m with you 😤❤️",
        "stress": "I'm hugging you through the stress 🤗💆‍♀️",
        "excited":"Yay! Tell me everything! 🎉💕",
        "proud":  "So proud of you 😭💖",
        "lost":   "Even when you feel lost, I’ll help you find your way 🧭",
        "default":"Hi baby 💖 I’m always here."
    }
    msg = messages.get(mood, messages["default"])
    uid = load_uid()
    if uid:
        bot.send_message(chat_id=uid, text=msg)
        return "Message sent 💌"
    return "No user ID yet — ask her to /start the bot first."

# === Set webhook and run Flask ===
async def setup():
    await tg_app.initialize()
    webhook_url = f"{APP_URL.rstrip('/')}/{WEBHOOK_PATH}"
    await bot.set_webhook(url=webhook_url)
    print("📡 Webhook set to:", webhook_url)

if __name__ == "__main__":
    asyncio.run(setup())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))