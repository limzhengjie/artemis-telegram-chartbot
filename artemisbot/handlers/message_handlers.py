from typing import List
from telegram import Update, Message, Bot
from telegram.ext import ContextTypes
from artemisbot.utils.command_parser import parse_command
from artemisbot.chart.url_builder import build_chart_url
from artemisbot.chart.screenshot import take_screenshot
from artemisbot.utils.asset_mappings import get_asset_by_id, get_asset_by_symbol


async def process_chart_command(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                      metric: str, tickers_raw: List[str], asset_type: str, 
                      time_period: str, granularity: str, is_percentage: bool,
                      is_group: bool = False) -> None:
    """
    Process a chart command and respond with the appropriate chart.
    
    Args:
        update: Telegram update object
        context: Telegram context object
        metric: Chart metric (fees, tvl, etc.)
        tickers_raw: List of tickers to chart
        asset_type: Asset type (CHAIN, APPLICATION, etc.)
        time_period: Time period for the chart
        granularity: Data granularity
        is_percentage: Whether to display as percentages
        is_group: Whether this is a group chat message
    """
    # Get asset names for display
    asset_names = []
    for ticker in tickers_raw:
        asset_info = get_asset_by_id(ticker) or get_asset_by_symbol(ticker)
        asset_names.append(asset_info["name"] if asset_info and "name" in asset_info else ticker.capitalize())
    
    ticker_display = "/".join(asset_names)
    
    # Create a readable title
    metric_display = {
        "price": "Price",
        "volume": "Volume",
        "tvl": "TVL",
        "fees": "Fees",
        "revenue": "Revenue",
        "mc": "Market Cap",
        "txns": "Transactions",
        "daa": "Daily Active Addresses",
        "dau": "Daily Active Users",
        "fdmc": "Fully Diluted Market Cap"
    }.get(metric, metric.capitalize())
    
    time_period_display = {
        "1w": "1 Week",
        "mtd": "Month to Date",
        "1m": "1 Month",
        "3m": "3 Months",
        "6m": "6 Months",
        "ytd": "Year to Date",
        "1y": "1 Year",
        "all": "All Time"
    }.get(time_period, time_period)
    
    granularity_display = {
        "1d": "Daily",
        "1w": "Weekly",
        "1m": "Monthly"
    }.get(granularity, granularity)
    
    title = f"{metric_display} - {ticker_display} ({time_period_display}, {granularity_display})"
    if is_percentage:
        title += " (%)"
    
    status_message = await update.message.reply_text(f"📊 Generating {title}...")
    
    try:
        # Build and process chart
        chart_url = build_chart_url(metric, tickers_raw, asset_type, time_period, granularity, is_percentage)
        
        screenshot_result = take_screenshot(chart_url)
        
        # Handle error responses
        if isinstance(screenshot_result, str) and screenshot_result.startswith("ERROR:"):
            error_code = screenshot_result.split(":")[1]
            await status_message.delete()
            
            if error_code == "AUTH_REQUIRED":
                await update.message.reply_text(
                    "🔒 Authentication Required\n\n"
                    "Please contact your administrator for access."
                )
            elif error_code == "NO_DATA":
                await update.message.reply_text(
                    f"📈 No Chart Data Available\n\n"
                    f"I couldn't find any {metric_display} data for {ticker_display}.\n\n"
                    f"Try different time periods (1m, 3m, 1y) or metrics (price, tvl, fees)."
                )
            elif error_code == "INVALID_PARAMETERS":
                prefix = "=art " if is_group else ""
                await update.message.reply_text(
                    f"⚠️ Invalid Chart Parameters\n\n"
                    f"Format: {prefix}<metric> <asset> <time_period> <granularity> [%]\n"
                    f"Example: {prefix}price solana 1w 1d"
                )
            else:
                await update.message.reply_text(
                    f"🛠️ Chart Generation Failed\n\n"
                    f"Please try again later or with different parameters."
                )
            return
        
        # Send successful chart
        await update.message.reply_photo(
            photo=screenshot_result,
            caption=title
        )
        await status_message.delete()
        
    except Exception as e:
        await status_message.delete()
        await update.message.reply_text(
            f"❌ Error: {str(e)}\n\n"
            f"Please try again later."
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Process incoming messages and generate charts based on user commands.
    """
    message_text = update.message.text.strip()
    parts = message_text.split()
    
    # Only process messages that start with a valid metric
    valid_metrics = ["price", "volume", "tvl", "fees", "revenue", "mc", "txns", "daa", "dau", "fdmc"]
    if len(parts) < 4:
        return
        
    # If the first word is not a valid metric, ignore the message completely
    if parts[0].lower() not in valid_metrics:
        return
    
    try:
        metric, tickers_raw, asset_type, time_period, granularity, is_percentage = parse_command(message_text)
        
        await process_chart_command(
            update, context, metric, tickers_raw, asset_type, time_period, granularity, is_percentage
        )
    except ValueError as e:
        try:
            await update.message.reply_text(
                f"Error: {str(e)}\n\n"
                f"Format: <metric> <asset> <time_period> <granularity> [%]\n"
                f"Example: price solana 1w 1d"
            )
        except Exception as reply_error:
            pass


async def handle_group_message(message: Message, bot: Bot) -> None:
    """Handle messages in group chats."""
    # Only process messages that start with '=art'
    if not message.text or not message.text.startswith('=art'):
        return
        
    # Remove the '=art' prefix and process the command
    command_text = message.text[4:].strip()
    if not command_text:
        return
        
    parts = command_text.split()
    if len(parts) < 4:
        return
        
    # Only process messages that start with a valid metric
    valid_metrics = ["price", "volume", "tvl", "fees", "revenue", "mc", "txns", "daa", "dau", "fdmc"]
    if parts[0].lower() not in valid_metrics:
        return
        
    try:
        metric, tickers_raw, asset_type, time_period, granularity, is_percentage = parse_command(command_text, is_group=True)
        
        # Create a fake update object for process_chart_command
        update = Update(0, message=message)
        context = ContextTypes.DEFAULT_TYPE()
        context.bot = bot
        
        await process_chart_command(
            update, context, metric, tickers_raw, asset_type, time_period, granularity, is_percentage, is_group=True
        )
    except ValueError as e:
        try:
            await message.reply_text(
                f"Error: {str(e)}\n\n"
                f"Format: =art <metric> <asset> <time_period> <granularity> [%]\n"
                f"Example: =art price solana 1w 1d"
            )
        except Exception as reply_error:
            pass


async def welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send a welcome message when the bot is added to a group chat.
    
    Args:
        update: Telegram update
        context: CallbackContext
    """
    try:
        # Make sure we have the required attributes
        if not update or not update.message or not update.message.new_chat_members:
            return
            
        # Get information about the new member
        new_members = update.message.new_chat_members
        
        # Get our bot's user ID
        try:
            bot_id = context.bot.id
        except (AttributeError, Exception) as e:
            return
        
        # Only proceed if our bot is one of the new members
        if any(member.id == bot_id for member in new_members):
            # Get the chat name for a personalized welcome
            chat_name = update.effective_chat.title or "this group" if update.effective_chat else "this group"
            
            # Send a beautifully formatted welcome message
            await update.message.reply_text(
                f"🌟 *Hello {chat_name}!* 🌟\n\n"
                f"Thanks for adding me to your group! I'm your Artemis Analytics Chart Bot, ready to generate beautiful crypto market visualizations right here in the chat.\n\n"
                
                f"📈 *What I can do for you:*\n"
                f"Generate charts for fees, price, volume, TVL, revenue, and more for various crypto assets.\n\n"
                
                f"👉 *How to use me:*\n"
                f"Just type `=art` followed by your chart request, like:\n\n"
                
                f"```\n"
                f"=art fees ethereum eth chain 1m 1d\n"
                f"=art price solana sol chain 3m\n"
                f"=art tvl uniswap uni application 1y 1w\n"
                f"```\n\n"
                
                f"The format is: `=art <metric> <artemis_id> <symbol> <asset_type> <time_period> [granularity]`\n\n"
                
                f"👋 Get started by trying one of the examples above!\n"
                f"📖 For more details, any member can message me directly with /help",
                parse_mode="Markdown"
            )
    except Exception as e:
        pass


async def command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Redirects commands to the appropriate handlers.
    
    Args:
        update: Telegram update
        context: CallbackContext
    """
    # Extract the command
    command = update.message.text.split()[0][1:].lower()  # Remove '/' and make lowercase
    
    # Route to the appropriate handler
    if command == 'start':
        await start_command(update, context)
    elif command == 'help':
        await help_command(update, context)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /start command - welcome new users.
    
    Args:
        update: Telegram update
        context: CallbackContext
    """
    await update.message.reply_text(
        "🔍 Welcome to Artemis Analytics Chart Bot! 📊\n\n"
        "I can generate charts from Artemis Analytics for you.\n\n"
        "The command format is:\n"
        "<metric> <artemis_id> <symbol> <asset_type> <time_period> [granularity] [options]\n\n"
        "Example: fees ethereum eth chain 1w 1d\n"
        "In group chats, start with 'art', like: art fees ethereum eth chain 1w 1d\n"
        "For more details, use /help"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /help command - provide detailed instructions.
    
    Args:
        update: Telegram update
        context: CallbackContext
    """
    await update.message.reply_text(
        "📊 Artemis Analytics Chart Bot\n\n"
        "Format: <metric> <asset> <time_period> <granularity> [%]\n\n"
        "Examples:\n"
        "• price solana 1w 1d\n"
        "• fees ethereum 3m 1d\n"
        "• tvl bitcoin 1y 1w %\n\n"
        "Metrics: price, volume, tvl, fees, revenue, mc, tx, fc\n"
        "Time Periods: 1w, mtd, 1m, 3m, 6m, ytd, 1y, all\n"
        "Granularity: 1d, 1w, 1m\n\n"
        "In group chats, start with 'art '",
        parse_mode='Markdown'
    )