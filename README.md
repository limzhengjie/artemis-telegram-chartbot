# Artemis Telegram Chart Bot

A Telegram bot that generates charts from Artemis Analytics data. This bot allows users to create beautiful charts for various crypto metrics directly in Telegram.

## 🌟 Features

- **Rich Chart Generation**: Create charts for various crypto metrics (price, volume, TVL, fees, revenue, etc.)
- **Multi-Asset Comparison**: Compare multiple cryptocurrencies on the same chart
- **Flexible Time Periods**: Select from various time periods (1d, 1w, 1m, 3m, 6m, 1y, all)
- **Customizable Granularity**: Choose different data granularities (1h, 1d, 1w, 1m)
- **Percentage Mode**: View data in raw values or as percentage changes
- **Group Chat Support**: Use in both private chats and group conversations
- **Friendly Error Handling**: User-friendly error messages for improved UX
- **Beautiful Welcome Messages**: Customized group chat welcome message

## 🚀 Quick Start

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/artemis-telegram-chartbot.git
cd artemis-telegram-chartbot
```

2. Create a `.env` file:
```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
ARTEMIS_API_KEY=your_artemis_api_key
```

3. Build and run with Docker Compose:
```bash
docker-compose up -d
```

### Manual Setup

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
python main.py
```

## 📝 Usage

### Command Format
```
<metric> <asset> <time_period> <granularity> [%]
```

### Examples
- `price solana 1w 1d` - Daily Solana price for the last week
- `fees ethereum 3m 1d` - Daily Ethereum fees for the last 3 months
- `tvl bitcoin 1y 1w %` - Weekly Bitcoin TVL as percentage for the last year

### Available Metrics
- `price` - Price charts
- `volume` - Trading volume
- `tvl` - Total Value Locked
- `fees` - Protocol fees
- `revenue` - Revenue
- `mc` - Market cap
- `txns` - Transaction count
- `daa` - Daily Active Addresses
- `dau` - Daily Active Users
- `fdmc` - Fully Diluted Market Cap

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

### Group Chat Usage
In group chats, start your command with `=art`:
```
=art price solana 1m 1d
```

## 🏗️ Architecture

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
│       ├── asset_mappings.py    # Asset data mappings
│       ├── command_parser.py    # Command parsing logic
│       └── config.py           # Configuration settings
├── config/                # Configuration files
├── logs/                  # Log files
├── tests/                 # Test files
├── main.py               # Bot entry point
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
└── requirements.txt      # Python dependencies
```

## 🚀 Deployment

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t artemis-telegram-chartbot .
```

2. Run the container:
```bash
docker run -d \
  --name artemis-bot \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e ARTEMIS_API_KEY=your_key \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/config:/app/config \
  artemis-telegram-chartbot
```

### Heroku Deployment

1. Create a new Heroku app:
```bash
heroku create your-app-name
```

2. Set environment variables:
```bash
heroku config:set TELEGRAM_BOT_TOKEN=your_token
heroku config:set ARTEMIS_API_KEY=your_key
```

3. Deploy:
```bash
git push heroku main
```

4. Scale the worker:
```bash
heroku ps:scale worker=1
```

## 🧪 Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Style
The project follows PEP 8 style guidelines. To check your code:
```bash
flake8 .
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For support, please open an issue in the GitHub repository.