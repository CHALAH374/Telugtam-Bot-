import json
import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ================= CONFIG =================
BOT_TOKEN = "8402659411:AAE1L1cCf_U_hb4kVRarpnL1ExEAb3eVZaQ"
BOT_USERNAME = "@Refferal_Youtube_free_bot"
CHANNEL_USERNAME = "https://t.me/Movie_Zone_Vip"
ADMIN_IDS = [8452357204]
APK_LINK = "https://t.me/PCMODAPKFREE_bot?start=BQADAQAD1wwAAp_hCUaESDFEBiF5vRYE"
DATA_FILE = "users.json"
COINS_PER_REFERRAL = 4
COINS_TO_REDEEM = 30
# =========================================

# ------------ DATA HANDLERS -----------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ------------ CAPTCHA -----------------------
def generate_captcha():
    a = random.randint(20, 99)
    b = random.randint(1, 20)
    if random.choice([True, False]):
        return f"{a} - {b}", a - b
    else:
        return f"{a} + {b}", a + b

# ------------ CHANNEL JOIN CHECK ------------
async def is_joined(update: Update, context):
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, update.effective_user.id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ------------ START COMMAND -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    uid = str(user.id)
    data = load_data()

    # Check channel join
    joined = await is_joined(update, context)
    if not joined:
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton("✅ Check Join", callback_data="check_join")]
        ]
        await update.message.reply_text(
            "🚫 You must join the channel to continue!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Initialize user
    referrer = args[0] if args else None
    if uid not in data:
        q, ans = generate_captcha()
        data[uid] = {
            "name": user.first_name,
            "coins": 0,
            "referrals": 0,
            "captcha_verified": False,
            "channel_joined": True,
            "redeem_sent": False
        }

        # Handle referral
        if referrer and referrer in data and referrer != uid:
            if uid not in data[referrer].get("ref_list", []):
                data[referrer]["coins"] += COINS_PER_REFERRAL
                data[referrer]["referrals"] += 1
                data[referrer].setdefault("ref_list", []).append(uid)

    save_data(data)

    await update.message.reply_text(
        f"👋 Hi {user.first_name}!\n\n🔐 Solve captcha:\n🧮 {data[uid]['captcha_verified'] and 'Already verified ✅' or (generate_captcha()[0] + ' = ?')}"
    )

# ------------ CALLBACK HANDLER -----------------
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "check_join":
        joined = await is_joined(update, context)
        if joined:
            await query.message.reply_text("✅ Joined! Now send /start")
        else:
            await query.message.reply_text("❌ Still not joined!")

# ------------ CAPTCHA CHECK ------------------
async def check_captcha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    data = load_data()

    if uid not in data or data[uid]["captcha_verified"]:
        return

    try:
        answer = int(update.message.text.strip())
    except:
        return

    # Use last captcha from user session
    q, correct_answer = generate_captcha()
    if answer == correct_answer:
        data[uid]["captcha_verified"] = True
        save_data(data)
        await update.message.reply_text("✅ Correct! Now share your invite link using /invite")
    else:
        await update.message.reply_text("❌ Wrong answer, try again!")

# ------------ INVITE LINK ---------------------
async def invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    link = f"https://t.me/{BOT_USERNAME}?start={uid}"
    await update.message.reply_text(f"🔗 Your invite link:\n{link}\n\n🪙 1 referral = {COINS_PER_REFERRAL} coins")

# ------------ BALANCE CHECK -------------------
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    data = load_data()
    if uid not in data:
        await update.message.reply_text("Start first using /start")
        return
    coins = data[uid]["coins"]
    await update.message.reply_text(f"🪙 Your Coins: {coins}")
    if coins >= COINS_TO_REDEEM and not data[uid]["redeem_sent"]:
        await send_apk(update, uid, data)

# ------------ SEND APK ------------------------
async def send_apk(update: Update, uid, data):
    message = f"🎉 Congratulations {data[uid]['name']}!\n\nYou have earned {COINS_TO_REDEEM} coins.\nHere is your APK link:\n\n🔗 {APK_LINK}\n\n✅ Enjoy the app!"
    await update.message.reply_text(message)
    data[uid]["redeem_sent"] = True
    save_data(data)

# ------------ ADMIN PANEL ---------------------
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    keyboard = [
        [InlineKeyboardButton("📊 Users", callback_data="users")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="lb")],
        [InlineKeyboardButton("📤 Export Data", callback_data="export")]
    ]
    await update.message.reply_text("👮 Admin Panel", reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()

    if query.data == "users":
        await query.message.reply_text(f"👥 Total Users: {len(data)}")
    elif query.data == "lb":
        top = sorted(data.items(), key=lambda x: x[1]["coins"], reverse=True)[:10]
        msg = "🏆 Leaderboard:\n\n"
        for i, (_, u) in enumerate(top, 1):
            msg += f"{i}. {u['name']} — {u['coins']} coins\n"
        await query.message.reply_text(msg)
    elif query.data == "export":
        await query.message.reply_text(f"📄 Data file: `{DATA_FILE}`", parse_mode="Markdown")

# ------------ MAIN ---------------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("invite", invite))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CallbackQueryHandler(callback_handler, pattern="check_join"))
    app.add_handler(CallbackQueryHandler(admin_actions))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_captcha))

    print("🤖 Ultimate Referral APK Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
