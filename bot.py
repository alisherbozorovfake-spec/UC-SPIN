import json
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import *
from spin import spin_handler

# ----------------- DATABASE -----------------
def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=2)

# ----------------- START -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    user = update.effective_user
    uid = str(user.id)

    if uid not in users:
        users[uid] = {
            "coins": DAILY_COIN,
            "last_daily": str(datetime.date.today()),
            "ref_used": False,
            "ref_from": context.args[0] if context.args else None,
            "ref_paid": False,
            "spins_today": 0,
            "last_spin_date": str(datetime.date.today()),
            "last_spin_time": 0
        }

    save_users(users)

    link = f"https://t.me/{context.bot.username}?start={uid}"

    keyboard = [
        [InlineKeyboardButton("🎡 Aylantirish (10 coin)", callback_data="spin")]
    ]

    await update.message.reply_text(
        f"👋 Salom {user.first_name}\n\n"
        f"🪙 Coin: {users[uid]['coins']}\n"
        f"🔗 Referal link:\n{link}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ----------------- DAILY -----------------
async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    uid = str(update.effective_user.id)
    today = str(datetime.date.today())

    if users[uid]["last_daily"] != today:
        users[uid]["coins"] += DAILY_COIN
        users[uid]["last_daily"] = today
        save_users(users)
        await update.message.reply_text("🎁 Sizga 10 coin berildi!")
    else:
        await update.message.reply_text("❌ Bugun coin oldingiz")

# ----------------- MAIN -----------------
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("daily", daily))
app.add_handler(CallbackQueryHandler(spin_handler, pattern="spin"))

app.run_polling()
