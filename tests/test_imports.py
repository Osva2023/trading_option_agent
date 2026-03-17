#!/usr/bin/env python3
"""Test script to validate all module imports"""

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

print("=" * 60)
print("IMPORT TEST - Trading Agent Project")
print("=" * 60)

tests_passed = 0
tests_failed = 0

# Test 1: Config
try:
    from config.settings import SYMBOLS, DATABASE_URI, POLL_INTERVAL
    print("✓ Config imports OK")
    print(f"  - Symbols: {SYMBOLS}")
    tests_passed += 1
except Exception as e:
    print(f"✗ Config imports failed: {e}")
    tests_failed += 1

# Test 2: Database
try:
    from src.database import MarketData, Alert, OptionsData, db, save_market_data
    print("✓ Database models OK")
    tests_passed += 1
except Exception as e:
    print(f"✗ Database models failed: {e}")
    tests_failed += 1

# Test 3: Utils
try:
    from src.utils import (
        setup_logging, get_historical_data, calculate_metrics, 
        classify_market, get_options_data, send_email, 
        is_market_open, sleep_until_next_window
    )
    print("✓ Utils functions OK")
    tests_passed += 1
except Exception as e:
    print(f"✗ Utils functions failed: {e}")
    tests_failed += 1

# Test 4: Backtest
try:
    from src.backtest import run_backtest, TradingStrategy
    print("✓ Backtest module OK")
    tests_passed += 1
except Exception as e:
    print(f"✗ Backtest module failed: {e}")
    tests_failed += 1

# Test 4b: Strategy layer
try:
    from src.strategies import StrategySignal, evaluate_strategy
    print("✓ Strategy layer OK")
    tests_passed += 1
except Exception as e:
    print(f"✗ Strategy layer failed: {e}")
    tests_failed += 1

# Test 5: Flask Web App
try:
    import py_compile
    py_compile.compile(os.path.join(PROJECT_ROOT, 'web/app.py'), doraise=True)
    print("✓ Flask app syntax OK")
    tests_passed += 1
except Exception as e:
    print(f"✗ Flask app failed: {e}")
    tests_failed += 1

# Test 6: Core trading_agent module
try:
    import py_compile
    py_compile.compile(os.path.join(PROJECT_ROOT, 'src/trading_agent.py'), doraise=True)
    print("✓ Trading agent syntax OK")
    tests_passed += 1
except Exception as e:
    print(f"✗ Trading agent script failed: {e}")
    tests_failed += 1

# Test 7: is_market_open function
try:
    from src.utils import is_market_open
    from datetime import datetime
    
    # Test with current time
    now = datetime.now()
    result = is_market_open(now)
    print(f"✓ is_market_open() function OK (current market open: {result})")
    tests_passed += 1
except Exception as e:
    print(f"✗ is_market_open() test failed: {e}")
    tests_failed += 1

# Test 8: Database initialization
try:
    from src.database import app as db_app
    with db_app.app_context():
        from src.database import db
        db.create_all()
    print("✓ Database initialization OK")
    tests_passed += 1
except Exception as e:
    print(f"✗ Database initialization failed: {e}")
    tests_failed += 1

print("\n" + "=" * 60)
print(f"RESULTS: {tests_passed} passed, {tests_failed} failed")
print("=" * 60)

if tests_failed == 0:
    print("✅ ALL TESTS PASSED!")
    sys.exit(0)
else:
    print("❌ SOME TESTS FAILED")
    sys.exit(1)
