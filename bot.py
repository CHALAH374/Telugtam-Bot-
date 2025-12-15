import asyncio
import re
import pytesseract
from PIL import Image
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = 35442064
API_HASH = "2ccfae0b01c89166657eb34f39392dcf"
BOT_TOKEN = "8384180043:AAEpcIoM9s_YRmF-MYkUY8KJRGvCzOh2KBk"

OWNER_CHANNEL = -1003401753390
YOUR_LINK = "https://t.me/Movie_Zone_Vip"
DELETE_AFTER = 7200

app = Client("promo_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_links = {}
waiting_ss = set()

PROMO_TEXT = f"""
🎬 Movie Lovers Special Alert 🔞

2025 අලුතින්ම Release උන
Tamil | English | Korean Movies
සිංහල උපසිරැසි සමඟ 🔥

⚠️ 18+ Viewers Only
👉 Join Now 👇
{YOUR_LINK}
"""

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply_text(
        "👋 Welcome!\n\n📎 ඔබගේ Channel Link එක එවන්න"
    )

@app.on_message(filters.text & filters.private)
async def get_link(client, message: Message):
    if message.from_user.id in waiting_ss:
        return

    link = message.text.strip()
    if not re.search(r"t\.me/", link):
        await message.reply("❌ Valid Telegram channel link එකක් එවන්න")
        return

    user_links[message.from_user.id] = link
    waiting_ss.add(message.from_user.id)

    promo = await message.reply_text(PROMO_TEXT)
    user_post = await message.reply_text(
        "📸 මේ post එක ඔයාගෙ channel එකට share කරලා\nScreenshot එක මෙතන send කරන්න"
    )

    asyncio.create_task(auto_delete(promo))
    asyncio.create_task(auto_delete(user_post))

async def auto_delete(msg):
    await asyncio.sleep(DELETE_AFTER)
    try:
        await msg.delete()
    except:
        pass

@app.on_message(filters.photo & filters.private)
async def check_screenshot(client, message: Message):
    uid = message.from_user.id
    if uid not in waiting_ss:
        return

    file = await message.download()
    text = pytesseract.image_to_string(Image.open(file))

    if YOUR_LINK.lower() in text.lower():
        await message.reply("✅ Verified! Thank you ❤️")

        caption = f"""
📢 New Promotion Post

🔗 Partner Channel:
{user_links.get(uid)}
"""

        await client.send_photo(
            chat_id=OWNER_CHANNEL,
            photo=file,
            caption=caption
        )

        waiting_ss.remove(uid)
        user_links.pop(uid, None)
    else:
        await message.reply(
            "❌ Screenshot එකේ අපේ link එක පේන නැහැ!\n\n"
            "👉 Correct Screenshot එකක් නැවත එවන්න"
    )
