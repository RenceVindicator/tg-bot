import os, json, asyncio
from flask import Flask, request, abort
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# === ENV Vars ===
BOT_TOKEN    = os.getenv("BOT_TOKEN")
APP_URL      = os.getenv("APP_URL", "http://localhost:5000")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "telegram")
USER_FILE    = "gf_id.json"

# === Telegram Setup ===
bot = Bot(token=BOT_TOKEN)
tg_app = Application.builder().token(BOT_TOKEN).build()

# === Save/Load GF user ID ===
def save_uid(uid: int):
    with open(USER_FILE, "w") as f:
        json.dump({"gf_id": uid}, f)

def load_uid():
    if not os.path.exists(USER_FILE):
        return None
    with open(USER_FILE) as f:
        return json.load(f).get("gf_id")

# === Telegram Command: /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    save_uid(uid)
    await update.message.reply_text("Hi love 💖 I'm ready to send you letters anytime!")
    print(f"✅ Saved user ID: {uid}")

tg_app.add_handler(CommandHandler("start", start))

# === Flask App ===
app = Flask(__name__)

# ✅ SYNC route — avoid Flask async crash
@app.post("/telegram")
async def telegram_webhook():
    if request.headers.get("content-type") != "application/json":
        return abort(415)

    update = Update.de_json(request.get_json(force=True), bot)

    # ✅ FIX: Schedule update using global event loop
    asyncio.run(tg_app.process_update(update))
    return "OK"

@app.get("/sendletter")
def send_letter():
    mood = request.args.get("mood", "default")
    messages = {
        "sad":    "Hi love 😢 just wanted to say I’m here for you 💖",
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
    return "No user ID yet — ask her to /start first."

# === Startup: Set Webhook ===
async def setup():
    await tg_app.initialize()  # ✅ Must be first
    webhook_url = f"{APP_URL.rstrip('/')}/{WEBHOOK_PATH}"
    await bot.set_webhook(url= "https://tg-bot-production-7d95.up.railway.app")
    print("📡 Webhook set to:", webhook_url)

if __name__ == "__main__":
    # 🚀 Make sure Telegram is fully initialized before Flask starts
    asyncio.run(setup())

    # ✅ Start the Flask app (after the bot is ready!)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))