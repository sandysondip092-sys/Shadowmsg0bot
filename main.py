import logging
import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
# I've put your token directly here as requested
TOKEN = "8761983039:AAEfPhjQUvHsICAunkeEr5JMKeuTO-iOxG8"
BOT_NAME = "Shadowmsg0bot"

# --- KEEP-ALIVE SERVER FOR RENDER ---
app = Flask(__name__)

@app.route('/')
def home():
    return f"{BOT_NAME} is running!"

def run_flask():
    # Render uses the PORT environment variable to listen for traffic
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- BOT LOGIC ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        target_id = context.args[0]
        context.user_data['target_id'] = target_id
        await update.message.reply_text("🤫 **Anonymous Mode Active!**\n\nSend your message now and I'll deliver it.")
    else:
        user_id = update.effective_user.id
        bot_info = await context.bot.get_me()
        link = f"https://t.me/{bot_info.username}?start={user_id}"
        await update.message.reply_text(
            f"👋 **Welcome to {BOT_NAME}!**\n\n"
            f"Share your link to get secret messages:\n`{link}`",
            parse_mode="Markdown"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_id = context.user_data.get('target_id')
    if target_id:
        try:
            await context.bot.send_message(
                chat_id=target_id, 
                text=f"📩 **New Anonymous Message:**\n\n{update.message.text}",
                parse_mode="Markdown"
            )
            await update.message.reply_text("✅ Message sent anonymously!")
            context.user_data.clear()
        except Exception as e:
            logging.error(f"Error sending message: {e}")
            await update.message.reply_text("❌ Could not send. The user might have blocked the bot.")
    else:
        await update.message.reply_text("I don't know who to send this to! Use a friend's link.")

def main():
    # Start the Flask web server in a background thread
    threading.Thread(target=run_flask, daemon=True).start()

    # Start the Telegram Bot polling
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print(f"{BOT_NAME} is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
