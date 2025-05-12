#!/usr/bin/env python3
"""
Artemis Analytics Telegram Chart Bot

A Telegram bot for generating and sharing charts from Artemis Analytics.
Command format: <metric> <artemis_id> <symbol> <asset_type> <time_period> [granularity] [options]

Example: fees ethereum eth chain 1w 1d
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables first
print("Loading environment variables...")
load_dotenv()

# Print current working directory and .env file location
print(f"Current working directory: {os.getcwd()}")
print(f"Looking for .env file in: {os.path.join(os.getcwd(), '.env')}")

# Verify required environment variables
required_vars = ['TELEGRAM_BOT_TOKEN', 'ARTEMIS_API_KEY']
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
    print("Please ensure these are set in your .env file")
    sys.exit(1)

print("Environment variables loaded successfully")

import signal
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from artemisbot.handlers.message_handlers import handle_message, handle_group_message, help_command

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    print("Received shutdown signal")
    sys.exit(0)

def main():
    """Start the bot."""
    print("Initializing bot...")
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create lock file
    lock_file = "/tmp/artemis_telegram_bot.lock"
    if os.path.exists(lock_file):
        print("Another instance is already running")
        sys.exit(1)
        
    with open(lock_file, "w") as f:
        f.write(str(os.getpid()))
    
    try:
        print("Creating Telegram application...")
        # Create the Application
        application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
        
        print("Adding handlers...")
        # Add handlers
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_group_message))
        
        # Start the bot
        print("Starting bot...")
        application.run_polling()
        
    except Exception as e:
        print(f"Error starting bot: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        # Clean up lock file
        if os.path.exists(lock_file):
            os.remove(lock_file)

if __name__ == "__main__":
    main()
