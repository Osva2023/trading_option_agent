import os
import sys
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (
    SYMBOLS, POLL_INTERVAL, BACKTEST_MODE, LOG_FILE, TEST_MODE,
    EMAIL_FROM, EMAIL_TO, PAPER_STARTING_CASH, POLYGON_API_KEY
)
from src.utils import (
    setup_logging, get_historical_data, calculate_metrics, classify_market,
    get_options_data, send_email, is_market_open, sleep_until_next_window
)
from src.database import (
    get_open_paper_position,
    get_paper_account_summary,
    save_alert,
    save_market_data,
    save_options_data,
)
from src.backtest import run_backtest
from src.paper_trading import execute_paper_signal, sync_paper_position
from src.alert_formatter import build_cycle_alert_email, format_symbol_update
from src.strategies import evaluate_strategy

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

        cycle_updates = []

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

            position = get_open_paper_position(symbol)
            if position:
                sync_paper_position(symbol, metrics['last_close'])

            strategy_context = {
                'position': position,
                'cash_available': get_paper_account_summary(PAPER_STARTING_CASH)['cash'],
                'now': now,
            }
            strategy_signal = evaluate_strategy(symbol, metrics, tags, strategy_context)
            paper_result = execute_paper_signal(strategy_signal)
            paper_note = ""
            if paper_result and paper_result.get('action') in {'opened', 'closed'}:
                paper_note = f" | Paper: {paper_result['action']} ({paper_result['reason']})"

            log_line = (
                f"{symbol} | Close: {metrics['last_close']} | "
                f"Vol: {metrics['current_vol']}% (hist {metrics['hist_vol']}%) | "
                f"IV Rank: {metrics['iv_rank']}% | ATR: {metrics['atr']} | "
                f"Tags: {', '.join(tags)} | {advice}{options_alert}{paper_note}"
            )

            print(log_line)

            previous_tags = last_tags.get(symbol)
            tag_changed = previous_tags is None or tags != previous_tags
            paper_event = paper_result and paper_result.get('action') in {'opened', 'closed'}

            if tag_changed or paper_event:
                symbol_message = format_symbol_update(
                    symbol=symbol,
                    previous_tags=previous_tags,
                    tags=tags,
                    metrics=metrics,
                    advice=advice,
                    options_info=options_info,
                    paper_result=paper_result,
                )
                cycle_updates.append({
                    'symbol': symbol,
                    'message': symbol_message,
                })
                save_alert(symbol, 'market_change', symbol_message)

            last_tags[symbol] = tags.copy()

        if cycle_updates:
            subject, body = build_cycle_alert_email(now, cycle_updates, TEST_MODE)
            send_email(subject, body)

        time.sleep(POLL_INTERVAL)

    except Exception as e:
        print(f"Error in main loop: {str(e)}")
        time.sleep(60)  # backoff