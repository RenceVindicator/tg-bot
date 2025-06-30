import os, json, asyncio
from flask import Flask, request, abort
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# =========  ENV VARIABLES you need on Railway =============
BOT_TOKEN      = os.getenv("BOT_TOKEN")                # already set
APP_URL        = os.getenv("APP_URL")                  # e.g. https://ikang-production.up.railway.app
WEBHOOK_PATH   = os.getenv("WEBHOOK_PATH", "telegram") # customise if you like
USER_FILE      = "gf_id.json"                          # stores her chat‑id
# =========================================================

bot  = Bot(token=BOT_TOKEN)
app  = Flask(__name__)                 # Flask instance
tg   = Application.builder().token(BOT_TOKEN).build()  # Telegram Application

# ---------- helper to store / load her chat‑id -------------
def save_uid(uid: int):
    with open(USER_FILE, "w") as f:
        json.dump({"gf_id": uid}, f)

def load_uid():
    if not os.path.exists(USER_FILE):
        return None
    with open(USER_FILE) as f:
        return json.load(f).get("gf_id")

# ---------- Telegram  /start  ------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    save_uid(uid)
    await update.message.reply_text("Hi love 💖 I'm ready to send you letters anytime!")
    print(f"✅ Saved user ID: {uid}")

tg.add_handler(CommandHandler("start", start))

# ---------- Webhook endpoint (Telegram -> Flask) ----------
@app.post(f"/{WEBHOOK_PATH}")
async def telegram_webhook():
    if request.headers.get("content-type") != "application/json":
        return abort(415)
    update = Update.de_json(request.get_json(force=True), bot)
    await tg.process_update(update)
    return "OK"

# ---------- Your /sendletter route  -----------------------
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
    return "No user ID yet — ask her to /start first."

# ---------- start‑up: set webhook then run Flask ----------
if __name__ == "__main__":
    # Tell Telegram where to send updates
    webhook_url = f"{APP_URL.rstrip('/')}/{WEBHOOK_PATH}"
    asyncio.run(bot.set_webhook(url=webhook_url))
    print("📡 Webhook set to:", webhook_url)

    # Run Flask (Railway maps PORT env var automatically)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))