#!/usr/bin/env python3
"""Quick syntax and basic structure check"""

import sys
import os
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

print("=" * 60)
print("PROJECT STRUCTURE & SYNTAX CHECK")
print("=" * 60)

# Check 1: Project files exist
required_files = [
    'config/settings.py',
    'src/trading_agent.py',
    'src/database.py',
    'src/utils.py',
    'src/backtest.py',
    'web/app.py',
    'requirements.txt',
    'README.md'
]

print("\nChecking required files:")
for file in required_files:
    path = os.path.join(PROJECT_ROOT, file)
    exists = "✓" if os.path.exists(path) else "✗"
    print(f"  {exists} {file}")

# Check 2: Python syntax validation
print("\nValidating Python syntax:")
python_files = [
    'config/settings.py',
    'src/trading_agent.py',
    'src/database.py',
    'src/utils.py',
    'src/backtest.py',
    'web/app.py',
    'run.py'
]

import py_compile
for file in python_files:
    path = os.path.join(PROJECT_ROOT, file)
    try:
        py_compile.compile(path, doraise=True)
        print(f"  ✓ {file}")
    except py_compile.PyCompileError as e:
        print(f"  ✗ {file}: {e}")

# Check 3: Config loaded
print("\nConfig validation:")
try:
    from config.settings import SYMBOLS, POLL_INTERVAL, BACKTEST_MODE
    print(f"  ✓ Config loaded")
    print(f"    - Symbols: {SYMBOLS}")
    print(f"    - Poll interval: {POLL_INTERVAL}s")
    print(f"    - Backtest mode: {BACKTEST_MODE}")
except Exception as e:
    print(f"  ✗ Config failed: {e}")

# Check 4: Database model compilation
print("\nDatabase validation:")
try:
    from src.database import MarketData, Alert, OptionsData
    print(f"  ✓ Database models loaded")
    print(f"    - MarketData table OK")
    print(f"    - Alert table OK")  
    print(f"    - OptionsData table OK")
except Exception as e:
    print(f"  ✗ Database failed: {e}")

print("\n" + "=" * 60)
print("✅ Basic project validation complete!")
print("=" * 60)
