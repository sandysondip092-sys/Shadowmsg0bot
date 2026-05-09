import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# TOKEN = "8761983039:AAEfPhjQUvHsICAunkeEr5JMKeuTO-iOxG8"

# Enable logging to see errors in the Render dashboard
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if user used a link like t.me/bot?start=12345
    if context.args:
        target_id = context.args[0]
        context.user_data['target_id'] = target_id
        await update.message.reply_text(
            "🤫 **Anonymous Mode Active!**\n\n"
            "Send me your message (text only) and I will deliver it without revealing your identity."
        )
    else:
        # Give the user their own link
        user_id = update.effective_user.id
        bot_username = (await context.bot.get_me()).username
        personal_link = f"https://t.me/{bot_username}?start={user_id}"
        
        await update.message.reply_text(
            f"👋 **Welcome to the Anonymous Bot!**\n\n"
            f"To receive secret messages, share your link:\n`{personal_link}`",
            parse_mode="Markdown"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_id = context.user_data.get('target_id')
    
    if target_id:
        try:
            # Send to the recipient
            await context.bot.send_message(
                chat_id=target_id,
                text=f"📩 **New Anonymous Message:**\n\n{update.message.text}",
                parse_mode="Markdown"
            )
            await update.message.reply_text("✅ Your message has been sent safely!")
            # Clear the target so the next message doesn't go to the same person by accident
            context.user_data.clear()
        except Exception as e:
            logging.error(f"Error: {e}")
            await update.message.reply_text("❌ I couldn't send that. The user may have blocked me.")
    else:
        await update.message.reply_text("I don't know who to send this to! Click someone's secret link first.")

def main():
    # Build the application
    application = Application.builder().token(TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
  
