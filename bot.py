const { Telegraf, Markup } = require('telegraf');

const bot = new Telegraf('8517103880:AAE8Jeng7XBicWQQt7eXjp6iz3iCmM_RMCA');

let postData = {};

bot.start((ctx) => {
    ctx.reply("👋 Welcome! Use /post to create a Telegram post with inline buttons.");
});

bot.command("post", (ctx) => {
    postData[ctx.from.id] = { step: 1 };
    ctx.reply("📝 *Enter Post Title:*", { parse_mode: "Markdown" });
});

// Step 1 - Title
bot.on("text", async (ctx) => {
    let id = ctx.from.id;
    if (!postData[id]) return;

    let step = postData[id].step;

    if (step === 1) {
        postData[id].title = ctx.message.text;
        postData[id].step = 2;
        return ctx.reply("✏️ *Enter description text:*", { parse_mode: "Markdown" });
    }

    if (step === 2) {
        postData[id].description = ctx.message.text;
        postData[id].step = 3;
        return ctx.reply("🔗 *Enter Button Text:*", { parse_mode: "Markdown" });
    }

    if (step === 3) {
        postData[id].buttonText = ctx.message.text;
        postData[id].step = 4;
        return ctx.reply("🌍 *Enter Button URL:*", { parse_mode: "Markdown" });
    }

    if (step === 4) {
        postData[id].buttonUrl = ctx.message.text;
        postData[id].step = 5;

        // Show preview
        ctx.reply(
            `📌 *Preview:*\n\n*${postData[id].title}*\n${postData[id].description}`,
            {
                parse_mode: "Markdown",
                reply_markup: {
                    inline_keyboard: [
                        [{
                            text: postData[id].buttonText,
                            url: postData[id].buttonUrl
                        }],
                        [{
                            text: "🚀 Send to Channel",
                            callback_data: "send_channel"
                        }]
                    ]
                }
            }
        );
    }
});

// Send to channel
bot.action("send_channel", async (ctx) => {
    let id = ctx.from.id;

    try {
        await ctx.telegram.sendMessage(
            "@YOUR_CHANNEL_USERNAME",
            `*${postData[id].title}*\n${postData[id].description}`,
            {
                parse_mode: "Markdown",
                reply_markup: {
                    inline_keyboard: [[{
                        text: postData[id].buttonText,
                        url: postData[id].buttonUrl
                    }]]
                }
            }
        );

        ctx.editMessageReplyMarkup(); // remove buttons
        ctx.reply("✅ Successfully sent to channel!");
        delete postData[id];

    } catch (err) {
        ctx.reply("❌ Error: Bot must be admin in your channel.");
    }
});

bot.launch();
console.log("Bot Running...");
