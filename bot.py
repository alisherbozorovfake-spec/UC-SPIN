import json
import random
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import *

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
            "ref_used": False
        }

        # REFERRAL
        if context.args:
            ref = context.args[0]
            if ref in users and not users[uid]["ref_used"]:
                users[ref]["coins"] += REF_COIN
                users[uid]["ref_used"] = True

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

# ----------------- DAILY COIN -----------------
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

# ----------------- SPIN -----------------
async def spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    users = load_users()
    uid = str(query.from_user.id)

    if users[uid]["coins"] < SPIN_COST:
        await query.message.reply_text("❌ Coin yetarli emas")
        return

    users[uid]["coins"] -= SPIN_COST

    chance = random.randint(1, 100)

    if chance <= 90:
        prize = "❌ Hech narsa"
    elif chance <= 97:
        prize = "🎁 15 ta Telegram hadiya"
        await context.bot.send_message(
            chat_id=ADMIN_USERNAME,
            text=f"🏆 G‘OLIB!\n\n👤 @{query.from_user.username}\n🎁 15 ta Telegram hadiya"
        )
    else:
        prize = "🔥 120 PUBG UC"
        await context.bot.send_message(
            chat_id=ADMIN_USERNAME,
            text=f"🏆 G‘OLIB!\n\n👤 @{query.from_user.username}\n🔥 120 PUBG UC"
        )

    save_users(users)

    await query.message.reply_text(
        "🎡 G‘ildirak aylanmoqda...\n\n"
        "⏳ 3...\n⏳ 2...\n⏳ 1...\n\n"
        f"🏁 Natija: {prize}"
    )

# ----------------- MAIN -----------------
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("daily", daily))
app.add_handler(CallbackQueryHandler(spin, pattern="spin"))

app.run_polling()
