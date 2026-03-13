# Trading Agent - CLI & Docker Guide

## Quick Start

### Test the Agent (Most Important)
```bash
./cli.sh test
```
This will verify the agent works correctly and can fetch market data.
It runs the full test suite with a single command.

---

## CLI Commands

All commands use the convenient `./cli.sh` script. Run `./cli.sh help` to see all available commands.

### Setup
```bash
# One-time setup
./cli.sh setup
```
- Creates virtual environment
- Installs all dependencies
- Installs python-dotenv for secure credential loading

### Testing & Development

#### Run Test
```bash
./cli.sh test
```
**Output shows:**
- ✅ Basic syntax and structure checks
- ✅ Import and database smoke checks
- ✅ Market data fetch success/failure
- ✅ Metrics and classification validation

```
TRADING AGENT TEST RUN
=====================
TEST_MODE: True
Symbols: ['SPY', 'QQQ', 'IWM', 'DIA', 'TLT']
Current time: 2026-03-09 17:02:38
Market open check: False

[TEST] Fetching market data for each symbol...

Testing SPY...
  ✅ SUCCESS
     - Price: $671.3
     - Volatility: 1.62%
     - IV Rank: -25.9%
     - Tags: TRENDING_DOWN, RANGE_BOUND, LOW_VOL

Testing QQQ...
  ✅ SUCCESS
```

#### Run Agent (TEST MODE - outside market hours)
```bash
./cli.sh run
```
- **TEST_MODE=True** in `.env` (default)
- Runs immediately, bypasses market hours check
- Processes all symbols every 5 minutes
- Great for testing and development

**Output:**
```
=== AGENT STARTED ===
Python version: 3.14.3
Current dir: /Users/grey/trading-agent-project
TEST_MODE: True
Entering main loop...
[TEST MODE] Running outside market hours...
Processing SPY
SPY | Close: $671.3 | Vol: 1.62% (hist 2.45%) | IV Rank: -25.9% | ATR: 4.21 | 
Tags: TRENDING_DOWN, RANGE_BOUND, LOW_VOL | Bearish trend...
[Alert Email Sent]
```

### Production Deployment

#### Run Agent (PRODUCTION MODE - respects market hours)
```bash
./cli.sh run-prod
```
- Requires **TEST_MODE=False** in `.env`
- Only runs during market hours:
  - 9:30-10:30 ET (Opening)
  - 12:00-13:00 ET (Midday)
  - 15:00-16:00 ET (Before close)
- Sleeps outside these windows
- Sends email alerts when tags change or high volatility detected

**Setup production mode:**
```bash
# In .env, change:
TEST_MODE=False
```

#### View Logs
```bash
./cli.sh logs
```
- Real-time log stream
- Shows all agent activity
- Press Ctrl+C to exit

---

## Docker Deployment

> **Why Docker?** Run the agent in a container for isolation, reproducibility, and easy deployment.

### Build Docker Image
```bash
./cli.sh docker-build
```
- Builds image from `docker/Dockerfile`
- Tagged as `trading-agent:latest`
- Includes all dependencies and configuration

### Run in Docker (Development)
```bash
./cli.sh docker-run
```
- Starts container with `docker-compose`
- Mounts `/data` directory for persistence
- Loads `.env` file automatically
- Flask dashboard available at `http://localhost:5001`

**Check if running:**
```bash
./cli.sh status
```

**View logs:**
```bash
docker logs -f trading-agent
```

### Stop Docker Container
```bash
./cli.sh docker-stop
```

### Manual Docker Commands

If you prefer not using the CLI script:

```bash
# Build
docker build -f docker/Dockerfile -t trading-agent:latest .

# Run
docker run -d \
  --name trading-agent \
  -p 5001:5001 \
  -v $(pwd)/data:/app/data \
  --env-file .env \
  trading-agent:latest

# View logs
docker logs -f trading-agent

# Stop
docker stop trading-agent
docker rm trading-agent
```

---

## Environment Variables

### Main Configuration (`.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `POLYGON_API_KEY` | (required) | Polygon.io API key |
| `ALPHA_VANTAGE_KEY` | (required) | Alpha Vantage API key |
| `EMAIL_FROM` | (required) | Sender email (Gmail) |
| `EMAIL_TO` | (required) | Recipient email |
| `EMAIL_PASS` | (required) | Gmail app password |
| `SYMBOLS` | SPY,QQQ,IWM,DIA,TLT | Trading symbols (comma-separated) |
| `POLL_INTERVAL` | 300 | Check interval in seconds |
| `TEST_MODE` | True | Bypass market hours (True=test, False=production) |
| `BACKTEST_MODE` | False | Run backtesting only |
| `BACKTEST_DAYS` | 30 | Days of historical data for backtesting |
| `FLASK_HOST` | 0.0.0.0 | Flask server host |
| `FLASK_PORT` | 5001 | Flask server port |

### Use `.env.example` as template
```bash
cp .env.example .env
# Then edit .env with your credentials
```

---

## Typical Workflows

### Development Workflow
```bash
# 1. Setup
./cli.sh setup

# 2. Test it works
./cli.sh test

# 3. Run with test mode
./cli.sh run

# 4. Keep TEST_MODE=True for development
# 5. Watch logs
./cli.sh logs
```

### Production Workflow
```bash
# 1. Set TEST_MODE=False in .env
nano .env  # or vim .env

# 2. Run production
./cli.sh run-prod

# 3. Will only run during market hours
# 4. Sends email alerts

# 5. Or deploy to Docker
./cli.sh docker-build
./cli.sh docker-run
./cli.sh status
```

### Docker Production
```bash
# Setup once
./cli.sh setup
./cli.sh test

# Build and run
./cli.sh docker-build
./cli.sh docker-run

# Monitor
docker logs -f trading-agent
./cli.sh status

# View dashboard
# Open http://localhost:5001 in browser
```

---

## Troubleshooting

### "Virtual environment not activated"
```bash
./cli.sh setup
source venv/bin/activate
```

### "TEST_MODE=True requires TEST_MODE=False for production"
```bash
# Edit .env
TEST_MODE=False
./cli.sh run-prod
```

### "No data returned" errors
- Check API keys in `.env`
- Verify internet connection
- Check logs with `./cli.sh logs`

### Docker port already in use
```bash
# Kill processes using port 5001
lsof -i :5001
kill -9 <PID>

# Then
./cli.sh docker-run
```

### Docker container won't start
```bash
docker logs trading-agent  # See full error
./cli.sh docker-stop       # Stop container
docker system prune        # Clean up
./cli.sh docker-build      # Rebuild
./cli.sh docker-run        # Restart
```

---

## Web Dashboard

Access the Flask dashboard at: **http://localhost:5001**

**Features:**
- Real-time market data display
- Recent alerts
- Options analysis
- Interactive data view

---

## Direct Python Commands

### One-liner tests
```bash
# Test imports
./venv/bin/python -c "from config.settings import SYMBOLS; print(SYMBOLS)"

# Run agent directly
./venv/bin/python run.py

# Run backtest only
./venv/bin/python -c "from src.backtest import run_backtest; run_backtest('SPY')"

# Quick market-data test only
./venv/bin/python tests/test_agent_run.py
```

### Interactive Python shell
```bash
source venv/bin/activate
python

# In Python shell:
from config.settings import SYMBOLS
from src.utils import get_historical_data, calculate_metrics
df = get_historical_data('SPY')
metrics = calculate_metrics(df)
print(metrics)
```

---

## Performance & Monitoring

### Monitor resource usage
```bash
# Docker stats
docker stats trading-agent

# System load
top
```

### Scaling
```bash
# For multiple symbols, edit .env:
SYMBOLS=SPY,QQQ,IWM,DIA,TLT,VIX,GLD,SLV

# Agent will process all sequentially
```

---

## Getting Help

```bash
./cli.sh help              # Show all CLI commands
./cli.sh test              # Verify setup is working
docker logs -f trading-agent  # Real-time container logs
cat data/logs/agent.log    # Check agent log file
```

---

**Last Updated:** March 13, 2026  
**Python Version:** 3.13+  
**Platform:** macOS / Linux / Docker
