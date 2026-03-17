#!/usr/bin/env python3
"""Deterministic tests for the explicit strategy layer."""

import os
import sys
from datetime import datetime
from types import SimpleNamespace

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.strategies import evaluate_strategy


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def base_metrics(**overrides):
    metrics = {
        'last_close': 100.0,
        'ema50': 99.0,
        'atr': 2.0,
        'rsi': 25.0,
    }
    metrics.update(overrides)
    return metrics


def base_context(**overrides):
    context = {
        'cash_available': 10000.0,
        'now': datetime(2026, 3, 17, 10, 0, 0),
    }
    context.update(overrides)
    return context


def test_entry_accepted():
    signal = evaluate_strategy('SPY', base_metrics(), ['TRENDING_UP', 'OVERSOLD'], base_context())
    assert_true(signal is not None, 'Expected entry signal')
    assert_true(signal.action == 'open', 'Expected open action')
    assert_true(signal.stop_loss == 98.0, 'Expected ATR-based stop loss')
    assert_true(signal.target_price == 104.0, 'Expected ATR-based target price')
    assert_true(signal.quantity == 10, 'Expected quantity sized from 10% cash budget')


def test_entry_rejected_by_trending_down():
    signal = evaluate_strategy('SPY', base_metrics(), ['OVERSOLD', 'TRENDING_DOWN'], base_context())
    assert_true(signal is None, 'Expected no signal while trending down')


def test_exit_by_rsi_recovery():
    position = SimpleNamespace(stop_loss=98.0, target_price=104.0, quantity=10)
    signal = evaluate_strategy(
        'SPY',
        base_metrics(rsi=58.0, last_close=103.0),
        ['TRENDING_UP', 'RSI_NEUTRAL'],
        base_context(position=position),
    )
    assert_true(signal is not None, 'Expected exit signal on RSI recovery')
    assert_true(signal.action == 'close', 'Expected close action')
    assert_true(signal.reason == 'RSI recovered to 58.00', 'Expected RSI recovery exit reason')


def test_exit_by_stop():
    position = SimpleNamespace(stop_loss=98.0, target_price=104.0, quantity=10)
    signal = evaluate_strategy(
        'SPY',
        base_metrics(last_close=97.5, rsi=40.0),
        ['TRENDING_UP'],
        base_context(position=position),
    )
    assert_true(signal is not None, 'Expected stop-loss exit signal')
    assert_true(signal.reason == 'Stop loss hit', 'Expected stop-loss reason')


def test_exit_by_target():
    position = SimpleNamespace(stop_loss=98.0, target_price=104.0, quantity=10)
    signal = evaluate_strategy(
        'SPY',
        base_metrics(last_close=104.5, rsi=40.0),
        ['TRENDING_UP'],
        base_context(position=position),
    )
    assert_true(signal is not None, 'Expected target exit signal')
    assert_true(signal.reason == 'Target price reached', 'Expected target reason')


def test_no_signal_with_missing_metrics():
    signal = evaluate_strategy('SPY', {'last_close': 100.0}, ['OVERSOLD'], base_context())
    assert_true(signal is None, 'Expected no signal with incomplete metrics')


def run_tests():
    tests = [
        test_entry_accepted,
        test_entry_rejected_by_trending_down,
        test_exit_by_rsi_recovery,
        test_exit_by_stop,
        test_exit_by_target,
        test_no_signal_with_missing_metrics,
    ]

    print('=' * 60)
    print('STRATEGY LAYER TESTS')
    print('=' * 60)

    for test in tests:
        test()
        print(f'✓ {test.__name__}')

    print('=' * 60)
    print('✅ Strategy layer tests passed')
    print('=' * 60)


if __name__ == '__main__':
    run_tests()