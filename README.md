# Trading Agent Project

A comprehensive trading analysis and automation system with market monitoring, backtesting, and web dashboard capabilities.

## Features

- **Real-time Market Monitoring**: Tracks multiple symbols with technical indicators
- **Options Analysis**: Fetches and analyzes options data for volatility insights
- **Backtesting Framework**: Test trading strategies on historical data
- **Email Alerts**: Automated notifications for market changes
- **Web Dashboard**: Real-time visualization of market data and alerts
- **Database Storage**: Persistent storage of all market data and alerts

## Project Structure

```
trading-agent-project/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── src/                         # Core source code
│   ├── __init__.py
│   ├── trading_agent.py         # Main monitoring script
│   ├── database.py              # Database models and functions
│   ├── backtest.py              # Backtesting logic
│   └── utils.py                 # Utility functions
├── web/                         # Web dashboard
│   ├── app.py                   # Flask application
│   └── templates/
│       └── dashboard.html
├── docker/                      # Containerization
│   └── Dockerfile
├── config/                      # Configuration
│   └── settings.py
├── data/                        # Data storage
│   └── logs/
└── tests/                       # Test suite (future)
```

## Setup

1. **Clone/Download** the project to your desired location
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Settings**: Edit `config/settings.py` with your API keys and preferences
4. **Run Locally**:
   ```bash
   python src/trading_agent.py
   ```
5. **Web Dashboard**: Access at `http://localhost:5000`

## Docker Usage

```bash
# Build container
docker build -t trading-agent ./docker

# Run monitoring
docker run -d -p 5001:5000 trading-agent

# Run backtesting
docker run trading-agent python src/trading_agent.py --backtest
```

## Configuration

Key settings in `config/settings.py`:
- `SYMBOLS`: List of symbols to monitor
- `POLL_INTERVAL`: Monitoring frequency (seconds)
- `BACKTEST_MODE`: Enable/disable backtesting
- API keys for data providers

## Database

- **Type**: SQLite (easily upgradeable to PostgreSQL)
- **Location**: `data/trading_agent.db`
- **Tables**: MarketData, Alert, OptionsData

Access database:
```bash
sqlite3 data/trading_agent.db
.schema
SELECT * FROM market_data LIMIT 5;
```

## Features Overview

### Market Analysis
- Exponential Moving Averages (20, 50, 200 periods)
- Volatility calculations (current vs historical)
- Average True Range (ATR)
- Implied Volatility Rank proxy
- Market classification (trending, range-bound, high/low vol)

### Options Integration
- Real-time options chain data
- At-the-money implied volatility analysis
- High IV alerts

### Alerting System
- Email notifications for market changes
- Configurable alert conditions
- Historical alert storage

### Backtesting
- Backtrader framework integration
- Custom strategy implementation
- Performance metrics and visualization

## Future Enhancements

- Automated trading integration
- Advanced strategy development
- Frontend dashboard improvements
- API endpoints for external integrations
- Machine learning predictions

## License

This project is for educational and personal use. Please comply with API provider terms of service.