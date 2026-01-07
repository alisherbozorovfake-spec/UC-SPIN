import random
import time
import datetime
from config import SPIN_COST, REF_COIN, ADMIN_USERNAME
from database import load_users, save_users


async def spin_handler(update, context):
    query = update.callback_query
    await query.answer()

    users = load_users()
    user = query.from_user
    uid = str(user.id)

    # ❌ USERNAME YO‘Q BO‘LSA
    if not user.username:
        await query.message.reply_text(
            "❌ Spin qilish uchun Telegram username qo‘yishingiz kerak!"
        )
        return

    # ❌ COIN YETARLI EMAS
    if users[uid]["coins"] < SPIN_COST:
        await query.message.reply_text("❌ Coin yetarli emas")
        return

    # ⏳ COOLDOWN (3 soniya)
    now = time.time()
    if now - users[uid]["last_spin_time"] < 3:
        await query.message.reply_text("⏳ Sekinroq! 3 soniya kuting")
        return

    users[uid]["last_spin_time"] = now

    # 📅 KUNLIK SPIN LIMITI
    today = str(datetime.date.today())
    if users[uid]["last_spin_date"] != today:
        users[uid]["spins_today"] = 0
        users[uid]["last_spin_date"] = today

    if users[uid]["spins_today"] >= 20:
        await query.message.reply_text("❌ Bugun spin limiti tugadi")
        return

    # 🪙 COIN AYIRISH
    users[uid]["coins"] -= SPIN_COST
    users[uid]["spins_today"] += 1

    # 🎯 OMAD HISOBI
    chance = random.randint(1, 100)

    if chance <= 90:
        prize = "❌ Hech narsa"
        win = False

    elif chance <= 97:
        prize = "🎁 15 ta Telegram hadiya"
        win = True

    else:
        prize = "🔥 120 PUBG UC"
        win = True

    # 🔗 REFERRAL BONUS (FAKAT 1 MARTA)
    ref = users[uid]["ref_from"]
    if ref and ref in users and not users[uid]["ref_paid"]:
        users[ref]["coins"] += REF_COIN
        users[uid]["ref_paid"] = True

    save_users(users)

    # 🏆 G‘OLIBNI ADMIN GA YUBORISH
    if win:
        await context.bot.send_message(
            chat_id=ADMIN_USERNAME,
            text=(
                "🏆 G‘OLIB!\n\n"
                f"👤 @{user.username}\n"
                f"🎁 Sovrin: {prize}"
            )
        )

    # 🎡 ANIMATSIYA
    await query.message.reply_text(
        "🎡 G‘ildirak aylanmoqda...\n"
        "⏳ 3...\n⏳ 2...\n⏳ 1...\n\n"
        f"🏁 Natija: {prize}"
    )
