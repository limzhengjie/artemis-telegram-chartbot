# Artemis Telegram Chart Bot

A Telegram bot that generates charts from Artemis Analytics data.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
export TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
export ARTEMIS_API_KEY="your_artemis_api_key"
```

3. Run the bot:
```bash
python3 main.py
```

## Usage

The bot supports the following command format:
```
<metric> <asset> <time_period> <granularity> [%]
```

Examples:
- `price solana 1w 1d`
- `fees ethereum 3m 1d`
- `tvl bitcoin 1y 1w %`

### Available Metrics
- `price` - Price charts
- `volume` - Trading volume
- `tvl` - Total Value Locked
- `fees` - Protocol fees
- `revenue` - Revenue
- `mc` - Market cap
- `tx` - Transaction count
- `fc` - Fully diluted value to revenue

### Time Periods
- `1w` - 1 week
- `mtd` - Month to date
- `1m` - 1 month
- `3m` - 3 months
- `6m` - 6 months
- `ytd` - Year to date
- `1y` - 1 year
- `all` - All time

### Granularity
- `1d` - Daily
- `1w` - Weekly
- `1m` - Monthly

### Options
- `%` - Show as percentage

In group chats, start your command with `art `:
```
art price solana 1m 1d
```

## 🌟 Features

- **Rich Chart Generation**: Create charts for various crypto metrics (price, volume, TVL, fees, revenue, etc.)
- **Multi-Asset Comparison**: Compare multiple cryptocurrencies on the same chart
- **Flexible Time Periods**: Select from various time periods (1d, 1w, 1m, 3m, 6m, 1y, all)
- **Customizable Granularity**: Choose different data granularities (1h, 1d, 1w, 1m)
- **Percentage Mode**: View data in raw values or as percentage changes
- **Group Chat Support**: Use in both private chats and group conversations
- **Friendly Error Handling**: User-friendly error messages for improved UX
- **Beautiful Welcome Messages**: Customized group chat welcome message

## 📋 Architecture

The bot is built with a modular, maintainable structure:

```
artemis-telegram-chartbot/
├── artemisbot/
│   ├── chart/             # Chart generation components
│   │   ├── screenshot.py  # Selenium screenshot capture
│   │   └── url_builder.py # Artemis URL construction
│   ├── handlers/          # Telegram message handlers
│   │   └── message_handlers.py  # Command processing
│   └── utils/             # Utility functions
│       ├── asset_helper.py      # Asset data helpers
│       ├── bot_setup.py         # Bot initialization
│       └── command_parser.py    # Command parsing logic
├── main.py                # Bot entry point
├── config.py              # Configuration settings
└── asset_mappings.py      # Asset ID mappings
```

## 🚀 Deployment

### Local Deployment

For local use, simply run:
```bash
python main.py
```