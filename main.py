import logging
import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 1. Background Server for Render
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    # Render provides a PORT environment variable automatically
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 2. Telegram Bot Logic
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        target_id = context.args[0]
        context.user_data['target_id'] = target_id
        await update.message.reply_text("🤫 **Anonymous Mode Active!** Send your message now.")
    else:
        user_id = update.effective_user.id
        bot_username = (await context.bot.get_me()).username
        link = f"https://t.me/{bot_username}?start={user_id}"
        await update.message.reply_text(f"👋 **Share this link to get secret messages:**\n`{link}`", parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_id = context.user_data.get('target_id')
    if target_id:
        try:
            await context.bot.send_message(chat_id=target_id, text=f"📩 **New Anonymous Message:**\n\n{update.message.text}", parse_mode="Markdown")
            await update.message.reply_text("✅ Sent!")
            context.user_data.clear()
        except Exception:
            await update.message.reply_text("❌ Failed. User might have blocked the bot.")
    else:
        await update.message.reply_text("Use a friend's link to send a message!")

def main():
    # Start the "keep-alive" server in a separate thread
    threading.Thread(target=run_flask, daemon=True).start()

    # Start the Telegram Bot
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
    
