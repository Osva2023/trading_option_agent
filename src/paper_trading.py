
from config.settings import PAPER_TRADING_ENABLED
from src.database import (
    close_paper_position,
    open_paper_position,
    update_paper_position_price,
)
def sync_paper_position(symbol, current_price):
    if not PAPER_TRADING_ENABLED:
        return None

    return update_paper_position_price(symbol, current_price)


def execute_paper_signal(signal):
    if not PAPER_TRADING_ENABLED or signal is None:
        return None

    signal_data = signal.to_dict() if hasattr(signal, 'to_dict') else dict(signal)
    action = signal_data.get('action')
    symbol = signal_data.get('symbol')

    if action == 'open':
        position = open_paper_position(
            symbol=symbol,
            strategy=signal_data.get('strategy', 'unknown_strategy'),
            entry_price=signal_data.get('entry_price'),
            quantity=signal_data.get('quantity'),
            stop_loss=signal_data.get('stop_loss'),
            target_price=signal_data.get('target_price'),
            entry_reason=signal_data.get('reason', ''),
        )
        if not position:
            return {
                'action': 'error',
                'symbol': symbol,
                'reason': 'Failed to open paper position',
            }

        return {
            **signal_data,
            'action': 'opened',
        }

    if action == 'close':
        trade = close_paper_position(symbol, signal_data.get('exit_price'), signal_data.get('reason', ''))
        if not trade:
            return {
                'action': 'error',
                'symbol': symbol,
                'reason': 'Failed to close paper position',
            }

        return {
            'action': 'closed',
            'symbol': symbol,
            'reason': signal_data.get('reason', ''),
            'trade': trade,
            'signal_id': signal_data.get('signal_id'),
            'strategy': signal_data.get('strategy'),
            'strategy_version': signal_data.get('strategy_version'),
            'tags': signal_data.get('tags', []),
            'rsi': signal_data.get('rsi'),
        }

        return {
            'action': 'error',
            'symbol': symbol,
            'reason': 'Unsupported signal action',
        }

