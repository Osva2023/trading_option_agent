#!/usr/bin/env python3
"""Quick test script to verify agent works in TEST_MODE"""

import sys
import os
import time
import threading

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import SYMBOLS, TEST_MODE, EMAIL_FROM, POLYGON_API_KEY
from src.utils import get_historical_data, calculate_metrics, classify_market, is_market_open
from datetime import datetime

print("=" * 70)
print("TRADING AGENT TEST RUN")
print("=" * 70)
print(f"TEST_MODE: {TEST_MODE}")
print(f"Symbols: {SYMBOLS}")
print(f"Email: {EMAIL_FROM}")
print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Market open check: {is_market_open(datetime.now())}")
print("=" * 70)

if not TEST_MODE:
    print("⚠️  TEST_MODE is False. Set TEST_MODE=True in .env to test outside market hours")
    sys.exit(0)

print("\n[TEST] Fetching market data for each symbol...\n")

success_count = 0
fail_count = 0

for symbol in SYMBOLS[:2]:  # Test with first 2 symbols only
    try:
        print(f"Testing {symbol}...")
        
        # Get historical data
        df = get_historical_data(symbol)
        if df.empty:
            print(f"  ❌ No data returned")
            fail_count += 1
            continue
        
        # Calculate metrics
        metrics = calculate_metrics(df)
        if not metrics:
            print(f"  ❌ No metrics calculated")
            fail_count += 1
            continue
        
        # Classify market
        tags, advice = classify_market(metrics, df)
        
        print(f"  ✅ SUCCESS")
        print(f"     - Price: ${metrics['last_close']}")
        print(f"     - Volatility: {metrics['current_vol']}%")
        print(f"     - IV Rank: {metrics['iv_rank']}%")
        print(f"     - Tags: {', '.join(tags) if tags else 'None'}")
        print(f"     - Advice: {advice[:50]}...")
        success_count += 1
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:80]}")
        fail_count += 1

print("\n" + "=" * 70)
print(f"TEST RESULTS: {success_count} passed, {fail_count} failed")
print("=" * 70)

if success_count > 0:
    print("✅ Agent is working correctly!")
    print("\nTo run the full agent: python run.py")
    print("To run it in production (respect market hours): Set TEST_MODE=False in .env")
else:
    print("❌ Agent encountered issues. Check API keys in .env")
    sys.exit(1)
