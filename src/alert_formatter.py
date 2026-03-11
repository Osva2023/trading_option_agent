from datetime import datetime


def build_manual_action(tags, metrics):
    if 'OVERSOLD' in tags and 'TRENDING_DOWN' not in tags:
        return 'Manual idea: watch for a mean-reversion long or paper long setup.'
    if 'OVERBOUGHT' in tags and 'TRENDING_UP' not in tags:
        return 'Manual idea: watch for a pullback, hedge, or avoid chasing longs.'
    if 'RANGE_BOUND' in tags and 'HIGH_VOL' in tags:
        return 'Manual idea: neutral defined-risk volatility setups may fit better than directional trades.'
    if 'RANGE_BOUND' in tags:
        return 'Manual idea: neutral or range-based setups fit better than breakout trades.'
    if 'TRENDING_UP' in tags and 'LOW_VOL' in tags:
        return 'Manual idea: bullish continuation setups are favored if price structure confirms.'
    if 'TRENDING_DOWN' in tags:
        return 'Manual idea: stay defensive, avoid forcing bullish entries against the trend.'
    return 'Manual idea: monitor only, no strong setup confirmation yet.'


def format_paper_action(paper_result):
    if not paper_result:
        return 'No paper trade action.'

    action = paper_result.get('action', 'none').upper()
    reason = paper_result.get('reason', 'No reason provided')

    if paper_result.get('action') == 'opened':
        quantity = paper_result.get('quantity', 0)
        entry_price = paper_result.get('entry_price', 0)
        return f'Paper trade: OPENED {quantity} shares at {entry_price:.2f}. {reason}'

    trade = paper_result.get('trade')
    if paper_result.get('action') == 'closed' and trade is not None:
        return (
            f'Paper trade: CLOSED {trade.quantity} shares at {trade.exit_price:.2f}. '
            f'P&L {trade.realized_pnl:.2f} ({trade.realized_pct:.2f}%). {reason}'
        )

    if paper_result.get('action') in {'held', 'skipped', 'error'}:
        return f'Paper trade: {action}. {reason}'

    return f'Paper trade: {action}. {reason}'


def format_symbol_update(symbol, previous_tags, tags, metrics, advice, options_info, paper_result):
    previous = ', '.join(previous_tags) if previous_tags else 'Initial snapshot'
    current = ', '.join(tags) if tags else 'No active tags'
    rsi_value = metrics.get('rsi')
    rsi_display = f'{rsi_value:.2f}' if rsi_value is not None else 'N/A'
    avg_call_iv = (options_info or {}).get('avg_call_iv')
    avg_put_iv = (options_info or {}).get('avg_put_iv')
    options_line = 'Options IV: unavailable'
    trade_ticket = format_trade_ticket(paper_result)
    if avg_call_iv is not None or avg_put_iv is not None:
        call_iv = f'{(avg_call_iv or 0) * 100:.1f}%'
        put_iv = f'{(avg_put_iv or 0) * 100:.1f}%'
        options_line = f'Options IV (call/put): {call_iv} / {put_iv}'

    lines = [
        f'Symbol: {symbol}',
        f'Previous tags: {previous}',
        f'Current tags: {current}',
        (
            f'Close: {metrics["last_close"]:.2f} | RSI: {rsi_display} | ATR: {metrics["atr"]:.2f} | '
            f'Vol: {metrics["current_vol"]:.2f}% (hist {metrics["hist_vol"]:.2f}%) | '
            f'IV Rank: {metrics["iv_rank"]:.1f}%'
        ),
        f'Advice: {advice}',
        build_manual_action(tags, metrics),
        options_line,
        format_paper_action(paper_result),
    ]
    if trade_ticket:
        lines.append(trade_ticket)
    return '\n'.join(lines)


def build_cycle_alert_email(cycle_time, cycle_updates, test_mode):
    symbols = ', '.join(update['symbol'] for update in cycle_updates)
    subject = f'Trading Agent Summary - {len(cycle_updates)} update(s): {symbols}'
    mode = 'TEST_MODE' if test_mode else 'PRODUCTION'
    header = [
        'Trading Agent Consolidated Alert',
        f'Time: {cycle_time.strftime("%Y-%m-%d %H:%M:%S")}',
        f'Mode: {mode}',
        f'Updated symbols: {len(cycle_updates)}',
        '',
    ]
    sections = []
    for update in cycle_updates:
        sections.append(update['message'])
        sections.append('-' * 72)
    body = '\n'.join(header + sections[:-1]) if sections else '\n'.join(header)
    return subject, body

def format_trade_ticket(paper_result):
    if not paper_result or paper_result.get('action') != 'opened':
        return None
    
    return '\n'.join([
        'Trade Ticket:',
        f"Signal ID: {paper_result.get('signal_id', 'N/A')}",
        f"Strategy: {paper_result.get('strategy_version', paper_result.get('strategy', 'N/A'))}",
        f"Entry: {paper_result.get('entry_price', 0):.2f}",
        f"Stop: {paper_result.get('stop_loss', 0):.2f}",
        f"Target: {paper_result.get('target_price', 0):.2f}",
        f"Quantity: {paper_result.get('quantity', 0)}",
    ])