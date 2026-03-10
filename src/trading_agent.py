import os
import sys
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (
    SYMBOLS, POLL_INTERVAL, BACKTEST_MODE, LOG_FILE, TEST_MODE,
    EMAIL_FROM, EMAIL_TO, POLYGON_API_KEY
)
from src.utils import (
    setup_logging, get_historical_data, calculate_metrics, classify_market,
    get_options_data, send_email, is_market_open, sleep_until_next_window
)
from src.database import save_market_data, save_alert, save_options_data
from src.backtest import run_backtest

print("=== AGENT STARTED ===")
print("Python version:", sys.version)
print("Current dir:", os.getcwd())
print("Log file path:", os.path.abspath(LOG_FILE))
print("POLYGON_API_KEY starts with:", POLYGON_API_KEY[:5] + '...' if POLYGON_API_KEY else "MISSING")
print("EMAIL_FROM:", EMAIL_FROM)
print("EMAIL_TO:", EMAIL_TO)
print("TEST_MODE:", TEST_MODE)

setup_logging()

if BACKTEST_MODE:
    print("Running backtest mode...")
    for symbol in SYMBOLS:
        print(f"Backtesting {symbol}")
        run_backtest(symbol)
    print("Backtest complete.")
    sys.exit(0)

# Import Flask app to start web server
from web.app import flask_thread

last_tags = {}  # Track tags per symbol
print("Entering main loop...")

# Main monitoring loop
while True:
    try:
        now = datetime.now()
        if not TEST_MODE and not is_market_open(now):
            sleep_seconds = sleep_until_next_window(now)
            print(f"Outside market windows — sleeping {sleep_seconds / 3600:.1f} hours")
            time.sleep(sleep_seconds)
            continue

        if TEST_MODE:
            print(f"[TEST MODE] Running outside market hours...")


        for symbol in SYMBOLS:
            print(f"Processing {symbol}")

            df = get_historical_data(symbol)
            if df.empty:
                print(f"No data for {symbol}")
                continue

            metrics = calculate_metrics(df)
            if not metrics:
                print(f"No metrics for {symbol}")
                continue

            tags, advice = classify_market(metrics, df)

            # Fetch options data
            options_info = get_options_data(symbol)
            options_alert = ""
            if options_info and options_info['avg_call_iv'] and options_info['avg_call_iv'] > 0.3:
                options_alert = f" | High Options IV: {options_info['avg_call_iv']:.2%}"

            # Save data to database
            save_market_data(symbol, metrics, tags)
            save_options_data(symbol, options_info)

            log_line = (
                f"{symbol} | Close: {metrics['last_close']} | "
                f"Vol: {metrics['current_vol']}% (hist {metrics['hist_vol']}%) | "
                f"IV Rank: {metrics['iv_rank']}% | ATR: {metrics['atr']} | "
                f"Tags: {', '.join(tags)} | {advice}{options_alert}"
            )

            print(log_line)

            # Alerta si tags cambiaron o high vol
            if symbol not in last_tags or tags != last_tags[symbol]:
                subject = f"{symbol} Market Alert - {', '.join(tags)}"
                body = f"{log_line}\nTime: {now.strftime('%Y-%m-%d %H:%M:%S')}"
                send_email(subject, body)
                save_alert(symbol, 'market_change', body)
                last_tags[symbol] = tags.copy()

        time.sleep(POLL_INTERVAL)

    except Exception as e:
        print(f"Error in main loop: {str(e)}")
        time.sleep(60)  # backoff