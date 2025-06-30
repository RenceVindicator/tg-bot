import os, json, asyncio
from flask import Flask, request, abort
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# === Config ===
BOT_TOKEN    = os.getenv("BOT_TOKEN")
APP_URL      = os.getenv("APP_URL")  # e.g. https://your-app.up.railway.app
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "telegram")
USER_FILE    = "gf_id.json"

# === Flask & Telegram ===
app = Flask(__name__)
tg_app = Application.builder().token(BOT_TOKEN).build()
bot = tg_app.bot  # get bot instance from tg_app

# === Save / load her ID ===
def save_uid(uid):
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
    print(f"✅ Saved ID: {uid}")

tg_app.add_handler(CommandHandler("start", start))

# === Webhook endpoint ===
@app.post(f"/{WEBHOOK_PATH}")
async def telegram_webhook():
    if request.headers.get("content-type") != "application/json":
        return abort(415)
    update = Update.de_json(request.get_json(force=True), bot)
    await tg_app.process_update(update)
    return "OK"

# === Web route for sending a mood message ===
@app.get("/reset")
def reset_user():
    if os.path.exists(USER_FILE):
        os.remove(USER_FILE)
        return "✅ User ID reset!"
    return "⚠️ No ID was saved."
@app.get("/sendletter")
async def send_letter():

    mood = request.args.get("mood", "default")
    messages = {
        "sad": "I'm here for you, love 😢💗",
        "happy": "You're glowing 🌟 and I love it!",
        "mad": "Whatever it is, I’m with you 😤❤️",
        "tired": "Rest well, love 💤",
        "stress": "Breathe, I got you 🤗",
        "excited": "I’m excited for you too 🎉💕",
        "proud": "So proud of you 😭💖",
        "lost": "Even if you feel lost, I’ll find you 🧭",
        "default": "Hi baby 💖 I’m always here."
    }

    uid = load_uid()
    text = messages.get(mood, messages["default"])

     if not uid:
        return "User ID not saved. Ask her to /start the bot."

    # Block until Telegram replies
    asyncio.run(bot.send_message(chat_id=uid, text=text))
    return "💌 Message sent!"

# === Startup logic ===
def setup_webhook():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(tg_app.initialize())
    webhook_url = f"{APP_URL.rstrip('/')}/{WEBHOOK_PATH}"
    loop.run_until_complete(bot.set_webhook(url=webhook_url))
    print("📡 Webhook set to:", webhook_url)

if __name__ == "__main__":
    setup_webhook()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))