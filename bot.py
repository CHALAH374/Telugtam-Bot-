from pyrogram import Client, filters
import random
import asyncio

API_ID = 35442064
API_HASH = "2ccfae0b01c89166657eb34f39392dcf"
BOT_TOKEN = "8516448938:AAFV1lA2iO1rTGu_syIOiYCmns2iJUGVN6o"

REACTIONS = ["🔥", "❤️", "👍", "😍", "👏", "😮"]

app = Client(
    "PublicAutoReactBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text(
        "🔥 **Public Auto React Bot**\n\n"
        "➕ Add me as **Admin** to your channel\n"
        "✅ Give **Add Reactions** permission\n"
        "💥 I will auto react to every post\n\n"
        "👨‍💻 Developed by CHALAH X BOT V3"
    )

@app.on_message(filters.command("help"))
async def help(_, message):
    await message.reply_text(
        "📌 **How to use:**\n\n"
        "1️⃣ Add bot to your channel\n"
        "2️⃣ Make bot admin\n"
        "3️⃣ Allow Add Reactions\n"
        "4️⃣ Done! 🎉\n\n"
        "🔥 Reactions will be added automatically"
    )

@app.on_message(filters.command("ping"))
async def ping(_, message):
    await message.reply_text("🏓 Pong! Bot is alive 🔥")

@app.on_message(filters.channel)
async def auto_react(_, message):
    try:
        reacts = random.sample(REACTIONS, 5)
        for emoji in reacts:
            await asyncio.sleep(1.5)  # Flood control
            await app.send_reaction(
                chat_id=message.chat.id,
                message_id=message.id,
                emoji=emoji
            )
    except Exception as e:
        print(e)

app.run()
