# Trading Agent - Quick Reference Card

## 🚀 Start Here (Copy & Paste)

### Test it Works (RIGHT NOW)
```bash
cd /Users/grey/trading-agent-project
./cli.sh test
```
✅ This proves the agent can fetch market data and works correctly.

---

## 🎯 3 Ways to Run

### Way 1: Development (TEST MODE - Runs Immediately)
```bash
./cli.sh run
```
- Runs ANY TIME of day
- Processes every 5 minutes
- Perfect for testing
- **DEFAULT** (TEST_MODE=True in .env)

### Way 2: Production (MARKET HOURS ONLY)
```bash
# First: Edit .env
# Change TEST_MODE=True to TEST_MODE=False

./cli.sh run-prod
```
- Only runs 9:30-10:30, 12:00-13:00, 15:00-16:00 ET
- Sleeps outside market hours
- Sends real email alerts
- Production-ready

### Way 3: Docker (Best for Deployment)
```bash
./cli.sh docker-build    # One-time build
./cli.sh docker-run      # Start container
./cli.sh status          # Check status
./cli.sh docker-stop     # Stop container
```
- Isolated, reproducible environment
- Easy deployment
- Dashboard at http://localhost:5001

---

## 📋 All CLI Commands

```bash
./cli.sh help             # Show this help
./cli.sh setup            # Install dependencies (one-time)
./cli.sh test             # Run full test suite (single command)
./cli.sh run              # Run agent (TEST_MODE)
./cli.sh run-prod         # Run agent (PRODUCTION)
./cli.sh logs             # View live logs
./cli.sh docker-build     # Build Docker image
./cli.sh docker-run       # Start Docker container
./cli.sh docker-stop      # Stop Docker container
./cli.sh status           # Show Docker status
```

---

## 🔧 Configuration

**File:** `.env`

Essential settings:
```
POLYGON_API_KEY=your_key_here
ALPHA_VANTAGE_KEY=your_key_here
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient@email.com
EMAIL_PASS=your_app_password
TEST_MODE=True              # True=test, False=production
SYMBOLS=SPY,QQQ,IWM,DIA,TLT
POLL_INTERVAL=300           # Check every 5 minutes
```

Change TEST_MODE to switch between dev and production.

---

## 📊 What Happens When You Run It

### Test Mode (./cli.sh run)
```
=== AGENT STARTED ===
TEST_MODE: True
Entering main loop...
[TEST MODE] Running outside market hours...

Processing SPY
  ✓ Close: $671.3
  ✓ Volatility: 1.62%
  ✓ Tags: TRENDING_DOWN, LOW_VOL
  ✓ Email alert sent

Processing QQQ
  ✓ Close: $598.8
  ✓ Volatility: 0.92%
  ✓ Tags: TRENDING_DOWN, LOW_VOL
  ✓ Email alert sent

[Repeats every 5 minutes...]
```

### Production Mode (./cli.sh run-prod)
```
Outside market windows — sleeping 16.8 hours
[Waits until 9:30 ET]
Processing SPY
  [Same output as above]
[Waits until polling interval]
```

---

## 📈 Features

✅ Real-time market data (Polygon.io API)  
✅ Technical analysis (EMA, ATR, Volatility, IV Rank)  
✅ Email alerts on market changes  
✅ Web dashboard (http://localhost:5001)  
✅ Backtesting framework  
✅ Database persistence (SQLite)  
✅ Market hour awareness  
✅ Docker containerization  

---

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| "Virtual environment not activated" | Run `./cli.sh setup` |
| "No data returned" | Check API keys in `.env` |
| "Port 5001 already in use" | Run `lsof -i :5001` then `kill -9 <PID>` |
| "Docker container won't start" | Run `docker logs trading-agent` to see error |
| Agent sleeps by default | Set `TEST_MODE=True` to run anytime |

---

## 📚 Documentation

- **Full Guide:** Read `CLI_DOCKER_GUIDE.md`
- **Project README:** Read `README.md`
- **API Keys:** See `config/settings.py` for configuration details
- **Logs:** Check `data/logs/agent.log` for detailed output

---

## 💻 Direct Commands (Without CLI Script)

```bash
# Activate virtual environment
source venv/bin/activate

# Run agent directly
python run.py

# Run specific tests directly
python tests/test_agent_run.py
python tests/test_manual.py

# View logs
tail -f data/logs/agent.log

# Access Python REPL
python
>>> from config.settings import SYMBOLS
>>> print(SYMBOLS)
```

---

## 🌐 Web Dashboard

**URL:** http://localhost:5001

After running the agent, visit the dashboard to see:
- Latest market data for each symbol
- Real-time alerts
- Historical data
- Options analysis

---

## ✅ Quick Verification

Did everything work?

```bash
# 1. Test works?
./cli.sh test
# → Should show "✅ Agent is working correctly!"

# 2. Agent runs?
./cli.sh run
# → Should show market data processing every 5 minutes
# → Press Ctrl+C to stop

# 3. Docker works?
./cli.sh docker-build
./cli.sh docker-run
docker logs -f trading-agent
# → Should show agent logs
```

---

**🎉 You're ready! Start with:** `./cli.sh test`

---

*Last Updated: March 13, 2026*  
*Platform: macOS / Linux / Docker*
