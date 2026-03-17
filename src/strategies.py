from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from config.settings import (
    ATR_STOP_MULTIPLIER,
    ATR_TARGET_MULTIPLIER,
    PAPER_POSITION_SIZE_PCT,
    RSI_ENTRY_THRESHOLD,
    RSI_EXIT_THRESHOLD,
    STRATEGY_ENABLED,
    STRATEGY_SYMBOLS,
)

STRATEGY_NAME = 'rsi_mean_reversion'
STRATEGY_VERSION = 'rsi_mean_reversion_v1'


@dataclass(frozen=True)
class StrategySignal:
    signal_id: str
    symbol: str
    action: str
    strategy: str
    strategy_version: str
    reason: str
    entry_price: float | None = None
    exit_price: float | None = None
    stop_loss: float | None = None
    target_price: float | None = None
    quantity: int | None = None
    rsi: float | None = None
    tags: tuple[str, ...] = ()

    def to_dict(self):
        data = asdict(self)
        data['tags'] = list(self.tags)
        return data


def evaluate_strategy(symbol, metrics, tags, context=None):
    if not STRATEGY_ENABLED or symbol not in STRATEGY_SYMBOLS or not metrics:
        return None

    price = metrics.get('last_close')
    if price is None or price <= 0:
        return None

    context = context or {}
    normalized_tags = tuple(tags or [])
    position = context.get('position')

    if position:
        return _evaluate_exit(symbol, metrics, normalized_tags, position, context)

    return _evaluate_entry(symbol, metrics, normalized_tags, context)


def build_signal_id(symbol, strategy_name, now=None):
    timestamp = (now or datetime.utcnow()).strftime('%Y%m%d%H%M')
    return f"{symbol}-{timestamp}-RSI1"


def get_position_size(price, cash_available):
    if price is None or price <= 0 or cash_available is None or cash_available <= 0:
        return 0

    budget = cash_available * PAPER_POSITION_SIZE_PCT
    quantity = int(budget // price)
    return max(quantity, 0)


def _evaluate_entry(symbol, metrics, tags, context):
    rsi = metrics.get('rsi')
    ema50 = metrics.get('ema50')
    atr = metrics.get('atr')
    price = metrics.get('last_close')

    if rsi is None or ema50 is None or atr is None:
        return None

    if 'OVERSOLD' not in tags:
        return None

    if 'TRENDING_DOWN' in tags:
        return None

    if rsi > RSI_ENTRY_THRESHOLD:
        return None

    if 'TRENDING_UP' not in tags and price < ema50:
        return None

    quantity = get_position_size(price, context.get('cash_available'))
    if quantity <= 0:
        return None

    stop_loss = round(price - (atr * ATR_STOP_MULTIPLIER), 2)
    target_price = round(price + (atr * ATR_TARGET_MULTIPLIER), 2)
    reason = (
        f"RSI {rsi:.2f} met entry threshold with tags: {', '.join(tags)}. "
        f"Price {price:.2f} vs EMA50 {ema50:.2f}."
    )

    return StrategySignal(
        signal_id=build_signal_id(symbol, STRATEGY_NAME, context.get('now')),
        symbol=symbol,
        action='open',
        strategy=STRATEGY_NAME,
        strategy_version=STRATEGY_VERSION,
        reason=reason,
        entry_price=price,
        stop_loss=stop_loss,
        target_price=target_price,
        quantity=quantity,
        rsi=rsi,
        tags=tags,
    )


def _evaluate_exit(symbol, metrics, tags, position, context):
    price = metrics.get('last_close')
    rsi = metrics.get('rsi')
    stop_loss = _position_value(position, 'stop_loss')
    target_price = _position_value(position, 'target_price')
    quantity = _position_value(position, 'quantity')

    if stop_loss is not None and price <= stop_loss:
        reason = 'Stop loss hit'
    elif target_price is not None and price >= target_price:
        reason = 'Target price reached'
    elif rsi is not None and rsi >= RSI_EXIT_THRESHOLD:
        reason = f'RSI recovered to {rsi:.2f}'
    elif 'TRENDING_DOWN' in tags:
        reason = 'Trend weakened to TRENDING_DOWN'
    else:
        return None

    return StrategySignal(
        signal_id=build_signal_id(symbol, STRATEGY_NAME, context.get('now')),
        symbol=symbol,
        action='close',
        strategy=STRATEGY_NAME,
        strategy_version=STRATEGY_VERSION,
        reason=reason,
        exit_price=price,
        stop_loss=stop_loss,
        target_price=target_price,
        quantity=quantity,
        rsi=rsi,
        tags=tags,
    )


def _position_value(position, field_name):
    if isinstance(position, dict):
        return position.get(field_name)
    return getattr(position, field_name, None)