#!/usr/bin/env python3
"""
Trading Agent Entry Point
Run this from the project root directory
"""
import os
import sys

# Ensure project root is in Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

if __name__ == '__main__':
    from src.trading_agent import *
