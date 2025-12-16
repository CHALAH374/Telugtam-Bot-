import json, os, random
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters
)

# ================= CONFIG =================
BOT_TOKEN = "8124366243:AAH5sLw7M07PaQROdNPrZsBS7jTUVZZSOuU"
BOT_USERNAME = "@Bybit_Refferal_Earn_Srilanka_bot"
CHANNEL_USERNAME = "@Movie_Zone_Vip"
ADMIN_IDS = [8452357204]
DATA_FILE = "users.json"
# =========================================

# ------------ DATA ------------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ------------ CAPTCHA ---------------------
def generate_captcha():
    a = random.randint(20, 99)
    b = random.randint(1, 20)
    if random.choice([True, False]):
        return f"{a} - {b}", a - b
    else:
        return f"{a} + {b}", a + b

# ------------ JOIN CHECK ------------------
async def is_joined(update: Update, context):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ------------ START -----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joined = await is_joined(update, context)
    if not joined:
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton("✅ Check Join", callback_data="check_join")]
        ]
        await update.message.reply_text(
            "🚫 **You must join our channel to continue!**",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

    user = update.effective_user
    args = context.args
    data = load_data()
    uid = str(user.id)
    ref = args[0] if args else None

    if uid not in data:
        q, ans = generate_captcha()
        data[uid] = {
            "name": user.first_name,
            "uid": None,
            "invited": [],
            "count": 0,
            "captcha": {
                "question": q,
                "answer": ans,
                "verified": False
            }
        }

        if ref and ref in data and ref != uid:
            if uid not in data[ref]["invited"]:
                data[ref]["invited"].append(uid)
                data[ref]["count"] += 1

    save_data(data)

    await update.message.reply_text(
        f"""👋 Hi {user.first_name}

🔐 **Captcha Solve කරන්න**
🧮 **{data[uid]['captcha']['question']} = ?**

✍️ Answer send කරන්න
"""
    )

# ------------ CALLBACK --------------------
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "check_join":
        joined = await is_joined(update, context)
        if joined:
            await query.message.reply_text("✅ Joined! Now send /start")
        else:
            await query.message.reply_text("❌ Still not joined!")

# ------------ CAPTCHA CHECK ---------------
async def check_captcha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    data = load_data()

    if uid not in data:
        return

    captcha = data[uid]["captcha"]
    if captcha["verified"]:
        return

    try:
        ans = int(update.message.text.strip())
    except:
        return

    if ans == captcha["answer"]:
        data[uid]["captcha"]["verified"] = True
        save_data(data)
        await update.message.reply_text(
            "✅ Correct!\n👉 `/submitUID <Bybit UID>` send කරන්න"
        )
    else:
        await update.message.reply_text("❌ Wrong answer!")

# ------------ UID -------------------------
async def submit_uid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    data = load_data()

    if not data[uid]["captcha"]["verified"]:
        await update.message.reply_text("🔐 Solve captcha first!")
        return

    if not context.args:
        await update.message.reply_text("Usage: `/submitUID 12345678`", parse_mode="Markdown")
        return

    data[uid]["uid"] = context.args[0]
    save_data(data)
    await update.message.reply_text("✅ UID Saved!\n👉 /invite")

# ------------ INVITE ----------------------
async def invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    link = f"https://t.me/{BOT_USERNAME}?start={uid}"
    await update.message.reply_text(f"🔗 Your Invite Link:\n\n{link}")

# ------------ ADMIN PANEL -----------------
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    keyboard = [
        [InlineKeyboardButton("📊 Users", callback_data="users")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="lb")],
        [InlineKeyboardButton("📤 Export Data", callback_data="export")]
    ]
    await update.message.reply_text(
        "👮 **Admin Panel**",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def admin_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()

    if query.data == "users":
        await query.message.reply_text(f"👥 Total Users: {len(data)}")

    elif query.data == "lb":
        top = sorted(data.items(), key=lambda x: x[1]["count"], reverse=True)[:5]
        msg = "🏆 Leaderboard\n\n"
        for i, (_, u) in enumerate(top, 1):
            msg += f"{i}. {u['name']} — {u['count']}\n"
        await query.message.reply_text(msg)

    elif query.data == "export":
        await query.message.reply_text(f"📄 Data file: `{DATA_FILE}`", parse_mode="Markdown")

# ------------ MAIN ------------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("submitUID", submit_uid))
    app.add_handler(CommandHandler("invite", invite))
    app.add_handler(CommandHandler("admin", admin))

    app.add_handler(CallbackQueryHandler(callback_handler, pattern="check_join"))
    app.add_handler(CallbackQueryHandler(admin_actions))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_captcha))

    print("🤖 Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
