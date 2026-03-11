
from config.settings import (
    PAPER_POSITION_SIZE_PCT,
    PAPER_RSI_ENTRY,
    PAPER_RSI_EXIT,
    PAPER_STARTING_CASH,
    PAPER_TRADING_ENABLED,
)
from src.database import (
    close_paper_position,
    get_open_paper_position,
    get_paper_account_summary,
    open_paper_position,
    update_paper_position_price,
)
from datetime import datetime

STRATEGY_NAME = 'rsi_mean_reversion'
STRATEGY_VERSION = 'rsi_mean_reversion_v1'


def should_open_long(metrics, tags):
    rsi = metrics.get('rsi')
    if rsi is None:
        return False
    if 'TRENDING_DOWN' in tags:
        return False
    return rsi <= PAPER_RSI_ENTRY and (
        'TRENDING_UP' in tags or metrics['last_close'] >= metrics['ema50']
    )


def get_position_size(price, cash_available):
    if price <= 0 or cash_available <= 0:
        return 0
    budget = cash_available * PAPER_POSITION_SIZE_PCT
    quantity = int(budget // price)
    return max(quantity, 0)


def build_entry_reason(metrics, tags):
    return (
        f"RSI {metrics.get('rsi')} below threshold with tags: {', '.join(tags)}. "
        f"Price {metrics['last_close']} vs EMA50 {metrics['ema50']}."
    )


def process_paper_signal(symbol, metrics, tags):
    if not PAPER_TRADING_ENABLED or not metrics:
        return None

    summary = get_paper_account_summary(PAPER_STARTING_CASH)
    price = metrics['last_close']
    position = get_open_paper_position(symbol)

    if position:
        update_paper_position_price(symbol, price)
        rsi = metrics.get('rsi')

        if position.stop_loss is not None and price <= position.stop_loss:
            trade = close_paper_position(symbol, price, 'Stop loss hit')
            return {
                'action': 'closed',
                'symbol': symbol,
                'reason': 'Stop loss hit',
                'trade': trade,
            }

        if position.target_price is not None and price >= position.target_price:
            trade = close_paper_position(symbol, price, 'Target price reached')
            return {
                'action': 'closed',
                'symbol': symbol,
                'reason': 'Target price reached',
                'trade': trade,
            }

        if rsi is not None and rsi >= PAPER_RSI_EXIT:
            trade = close_paper_position(symbol, price, f'RSI recovered to {rsi}')
            return {
                'action': 'closed',
                'symbol': symbol,
                'reason': f'RSI recovered to {rsi}',
                'trade': trade,
            }

        if 'TRENDING_DOWN' in tags:
            trade = close_paper_position(symbol, price, 'Trend weakened to TRENDING_DOWN')
            return {
                'action': 'closed',
                'symbol': symbol,
                'reason': 'Trend weakened to TRENDING_DOWN',
                'trade': trade,
            }

        return {
            'action': 'held',
            'symbol': symbol,
            'reason': 'Position remains open',
        }

    if not should_open_long(metrics, tags):
        return None

    quantity = get_position_size(price, summary['cash'])
    if quantity <= 0:
        return {
            'action': 'skipped',
            'symbol': symbol,
            'reason': 'Not enough available cash for a paper position',
        }

    atr = metrics.get('atr') or 0
    stop_loss = round(price - atr, 2) if atr else None
    target_price = round(price + (atr * 2), 2) if atr else None
    reason = build_entry_reason(metrics, tags)
    position = open_paper_position(
        symbol=symbol,
        strategy=STRATEGY_NAME,
        entry_price=price,
        quantity=quantity,
        stop_loss=stop_loss,
        target_price=target_price,
        entry_reason=reason,
    )
    if not position:
        return {
            'action': 'error',
            'symbol': symbol,
            'reason': 'Failed to open paper position',
        }
    signal_id = build_signal_id(symbol, STRATEGY_NAME)
    
    return {
        'action': 'opened',
        'signal_id': signal_id,
        'symbol': symbol,
        'strategy': STRATEGY_NAME,
        'strategy_version': STRATEGY_VERSION,
        'reason': reason,
        'quantity': quantity,
        'entry_price': price,
        'stop_loss': stop_loss,
        'target_price': target_price,
        'rsi': metrics.get('rsi'),
        'tags': tags,
    }

def build_signal_id(symbol, strategy_name, now=None):
    timestamp = (now or datetime.utcnow()).strftime('%Y%m%d%H%M')
    return f"{symbol}-{timestamp}-RSI1"

