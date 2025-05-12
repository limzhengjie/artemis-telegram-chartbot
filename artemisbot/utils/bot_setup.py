import os
import sys
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from artemisbot.handlers.message_handlers import handle_message, handle_group_message, help_command

def setup_singleton():
    """Ensure only one instance of the bot is running."""
    lock_file = "/tmp/artemis_telegram_bot.lock"
    if os.path.exists(lock_file):
        sys.exit(1)
        
    with open(lock_file, "w") as f:
        f.write(str(os.getpid()))

def setup_bot():
    """Set up the bot with all handlers."""
    # Create the Application
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    
    # Add handlers
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_group_message))
    
    return application
