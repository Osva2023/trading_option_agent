# Configuration settings for Trading Agent

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# API Keys (loaded from environment variables)
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY', '')
ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY', '')

# Email settings (loaded from environment variables)
EMAIL_FROM = os.getenv('EMAIL_FROM', '')
EMAIL_TO = os.getenv('EMAIL_TO', '')
EMAIL_PASS = os.getenv('EMAIL_PASS', '')

# Trading settings
SYMBOLS_STR = os.getenv('SYMBOLS', 'SPY,QQQ,IWM,DIA,TLT')
SYMBOLS = [s.strip() for s in SYMBOLS_STR.split(',')]
POLL_INTERVAL = int(os.getenv('POLL_INTERVAL', '300'))  # 5 minutes
BACKTEST_MODE = os.getenv('BACKTEST_MODE', 'False').lower() in ('true', '1', 'yes')
BACKTEST_DAYS = int(os.getenv('BACKTEST_DAYS', '30'))

# Database
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
os.makedirs(DATA_DIR, exist_ok=True)
DATABASE_FILE = os.path.join(DATA_DIR, 'trading_agent.db')
DATABASE_URI = f'sqlite:///{DATABASE_FILE}'

# Logging
LOG_DIR = os.path.join(DATA_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'agent.log')

# Flask Web Server
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', '5001'))

# Paper Trading
PAPER_TRADING_ENABLED = os.getenv('PAPER_TRADING_ENABLED', 'True').lower() in ('true', '1', 'yes')
PAPER_STARTING_CASH = float(os.getenv('PAPER_STARTING_CASH', '10000'))
PAPER_POSITION_SIZE_PCT = float(os.getenv('PAPER_POSITION_SIZE_PCT', '0.10'))
PAPER_RSI_ENTRY = float(os.getenv('PAPER_RSI_ENTRY', '30'))
PAPER_RSI_EXIT = float(os.getenv('PAPER_RSI_EXIT', '55'))

# Test Mode
TEST_MODE = os.getenv('TEST_MODE', 'False').lower() in ('true', '1', 'yes')