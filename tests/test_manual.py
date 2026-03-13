#!/usr/bin/env python3
"""
Manual Testing Suite for Trading Agent
Run this to validate core functionality without pytest
"""

import sys
import os
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test 1: Import all modules"""
    print("🧪 Test 1: Module Imports")
    try:
        from config.settings import SYMBOLS, POLYGON_API_KEY
        from src.utils import get_historical_data, calculate_metrics, classify_market
        from src.database import MarketData, Alert, OptionsData, PaperPosition, PaperTrade
        from src.backtest import run_backtest
        from src.alert_formatter import build_cycle_alert_email
        from src.paper_trading import process_paper_signal
        from web.app import flask_app
        print("   ✅ All imports successful")
        return True
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False

def test_config():
    """Test 2: Configuration loading"""
    print("🧪 Test 2: Configuration")
    try:
        from config.settings import SYMBOLS, POLYGON_API_KEY, EMAIL_FROM
        assert len(SYMBOLS) > 0, "No symbols configured"
        assert POLYGON_API_KEY, "No API key configured"
        assert EMAIL_FROM, "No email configured"
        print(f"   ✅ Config loaded: {len(SYMBOLS)} symbols, API key present")
        return True
    except Exception as e:
        print(f"   ❌ Config test failed: {e}")
        return False

def test_data_fetch():
    """Test 3: Data fetching"""
    print("🧪 Test 3: Data Fetching")
    try:
        from src.utils import get_historical_data
        df = get_historical_data('SPY', days=1)  # Small dataset
        assert not df.empty, "DataFrame is empty"
        assert 'close' in df.columns, "Missing close column"
        assert len(df) > 10, f"Only {len(df)} rows fetched"
        print(f"   ✅ Data fetched: {len(df)} rows for SPY")
        return True
    except Exception as e:
        print(f"   ❌ Data fetch failed: {e}")
        return False

def test_calculations():
    """Test 4: Technical calculations"""
    print("🧪 Test 4: Technical Calculations")
    try:
        from src.utils import get_historical_data, calculate_metrics, classify_market
        df = get_historical_data('SPY', days=2)
        metrics = calculate_metrics(df)
        assert metrics, "No metrics calculated"
        assert 'last_close' in metrics, "Missing last_close"
        assert 'current_vol' in metrics, "Missing volatility"

        tags, advice = classify_market(metrics, df)
        assert isinstance(tags, list), "Tags should be list"
        assert isinstance(advice, str), "Advice should be string"

        print(f"   ✅ Calculations: Vol={metrics['current_vol']}%, Tags={tags}")
        return True
    except Exception as e:
        print(f"   ❌ Calculations failed: {e}")
        return False

def test_database():
    """Test 5: Database operations"""
    print("🧪 Test 5: Database Operations")
    try:
        from src.database import MarketData, Alert, OptionsData, PaperPosition, PaperTrade, db
        from config.settings import DATABASE_URI

        # Test model creation
        assert MarketData, "MarketData model not available"
        assert Alert, "Alert model not available"
        assert OptionsData, "OptionsData model not available"
        assert PaperPosition, "PaperPosition model not available"
        assert PaperTrade, "PaperTrade model not available"

        print(f"   ✅ Database models: OK (URI: {DATABASE_URI.split('/')[-1]})")
        return True
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
        return False

def test_email():
    """Test 6: Email configuration (no actual send)"""
    print("🧪 Test 6: Email Configuration")
    try:
        from config.settings import EMAIL_FROM, EMAIL_TO
        from src.utils import send_email

        assert EMAIL_FROM, "No sender email"
        assert EMAIL_TO, "No recipient email"
        assert '@' in EMAIL_FROM, "Invalid sender email format"

        print(f"   ✅ Email config: {EMAIL_FROM} → {EMAIL_TO}")
        print("   ⚠️  Note: Actual email sending not tested (would require SMTP)")
        return True
    except Exception as e:
        print(f"   ❌ Email test failed: {e}")
        return False

def test_market_hours():
    """Test 7: Market hours logic"""
    print("🧪 Test 7: Market Hours Logic")
    try:
        from src.utils import is_market_open
        from datetime import datetime

        # Test with current time
        now = datetime.now()
        result = is_market_open(now)
        print(f"   ✅ Market hours: Currently {'open' if result else 'closed'}")

        # Test with known market time (weekday 10 AM ET)
        test_time = datetime(now.year, now.month, now.day, 10, 0, 0)
        if test_time.weekday() < 5:  # Weekday
            market_open = is_market_open(test_time)
            print(f"   ✅ Market hours test: 10 AM ET = {'open' if market_open else 'closed'}")

        return True
    except Exception as e:
        print(f"   ❌ Market hours test failed: {e}")
        return False

def test_paper_trading():
    """Test 8: Paper trading engine"""
    print("🧪 Test 8: Paper Trading Engine")
    try:
        from src.database import app, db, PaperPosition, PaperTrade
        from src.paper_trading import process_paper_signal

        entry_metrics = {
            'last_close': 100.0,
            'ema50': 99.0,
            'atr': 2.0,
            'rsi': 25.0,
        }
        exit_metrics = {
            'last_close': 104.5,
            'ema50': 101.0,
            'atr': 2.0,
            'rsi': 58.0,
        }

        with app.app_context():
            PaperTrade.query.delete()
            PaperPosition.query.delete()
            db.session.commit()

        opened = process_paper_signal('SPY', entry_metrics, ['TRENDING_UP', 'OVERSOLD'])
        assert opened and opened['action'] == 'opened', "Paper position did not open"

        closed = process_paper_signal('SPY', exit_metrics, ['TRENDING_UP', 'RSI_NEUTRAL'])
        assert closed and closed['action'] == 'closed', "Paper position did not close"

        with app.app_context():
            assert PaperPosition.query.count() == 0, "Open paper position was not cleared"
            assert PaperTrade.query.count() == 1, "Closed paper trade was not recorded"

        print("   ✅ Paper trading: open and close flow works")
        return True
    except Exception as e:
        print(f"   ❌ Paper trading test failed: {e}")
        return False

def test_alert_formatting():
    """Test 9: Consolidated alert formatting"""
    print("🧪 Test 9: Alert Formatting")
    try:
        from src.alert_formatter import build_cycle_alert_email, format_symbol_update

        metrics = {
            'last_close': 100.0,
            'rsi': 28.5,
            'atr': 2.0,
            'current_vol': 12.5,
            'hist_vol': 10.0,
            'iv_rank': 42.0,
        }
        paper_result = {
            'action': 'opened',
            'signal_id': 'SPY-20260311-095500-RSI1',
            'strategy': 'rsi_mean_reversion',
            'strategy_version': 'rsi_mean_reversion_v1',
            'reason': 'RSI setup triggered',
            'quantity': 10,
            'entry_price': 100.0,
            'stop_loss': 98.0,
            'target_price': 104.0,
        }
        message = format_symbol_update(
            symbol='SPY',
            previous_tags=['LOW_VOL'],
            tags=['TRENDING_UP', 'OVERSOLD'],
            metrics=metrics,
            advice='Potential bounce from oversold conditions.',
            options_info={'avg_call_iv': 0.22, 'avg_put_iv': 0.25},
            paper_result=paper_result,
        )
        subject, body = build_cycle_alert_email(datetime(2026, 3, 10, 15, 30, 0), [{'symbol': 'SPY', 'message': message}], True)

        assert 'Trading Agent Summary' in subject, 'Missing consolidated subject'
        assert 'Symbol: SPY' in body, 'Missing symbol section in email body'
        assert 'Paper trade: OPENED' in body, 'Missing paper trade action in email body'
        assert 'Manual idea:' in body, 'Missing manual action guidance in email body'
        assert 'Trade Ticket:' in body, 'Missing trade ticket block in email body'
        assert 'Signal ID: SPY-20260311-095500-RSI1' in body, 'Missing signal ID in trade ticket'
        assert 'Strategy: rsi_mean_reversion_v1' in body, 'Missing strategy version in trade ticket'
        assert 'Entry: 100.00' in body, 'Missing entry price in trade ticket'
        assert 'Stop: 98.00' in body, 'Missing stop loss in trade ticket'
        assert 'Target: 104.00' in body, 'Missing target price in trade ticket'
        assert 'Quantity: 10' in body, 'Missing quantity in trade ticket'

        # Verify ticket is NOT present for non-opened actions
        closed_result = {'action': 'closed', 'reason': 'Stop loss hit', 'trade': None}
        message_closed = format_symbol_update(
            symbol='SPY', previous_tags=['OVERSOLD'], tags=['TRENDING_DOWN'],
            metrics=metrics, advice='Exit.', options_info=None, paper_result=closed_result,
        )
        assert 'Trade Ticket:' not in message_closed, 'Trade ticket should not appear for closed action'

        print('   ✅ Alert formatting: consolidated email and trade ticket content correct')
        return True
    except Exception as e:
        print(f"   ❌ Alert formatting test failed: {e}")
        return False

def run_all_tests():
    """Run all manual tests"""
    print("=" * 60)
    print("🧪 MANUAL TESTING SUITE - Trading Agent")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    tests = [
        test_imports,
        test_config,
        test_data_fetch,
        test_calculations,
        test_database,
        test_email,
        test_market_hours,
        test_paper_trading,
        test_alert_formatting
    ]

    passed = 0
    failed = 0

    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
        print()

    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed == 0:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Your trading agent is working correctly.")
        print()
        print("Next steps:")
        print("• Run: ./cli.sh run    (TEST_MODE)")
        print("• Run: ./cli.sh run-prod  (Production)")
        print("• Build features on dev branch")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        print("Check the errors above and fix configuration.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)