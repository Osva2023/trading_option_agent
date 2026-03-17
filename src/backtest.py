import os
import sys
import backtrader as bt
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import get_historical_data, calculate_metrics, classify_market
from config.settings import BACKTEST_DAYS
from src.strategies import evaluate_strategy

class TradingStrategy(bt.Strategy):
    def __init__(self):
        self.order = None
        self.active_trade_risk = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        self.order = None

        if order.status in [order.Completed] and order.isbuy() and self.active_trade_risk:
            # Keep risk anchors tied to the filled entry price.
            fill_price = order.executed.price
            atr = self.active_trade_risk.get('atr', 0)
            if atr and fill_price:
                self.active_trade_risk['stop_loss'] = round(fill_price - atr, 2)
                self.active_trade_risk['target_price'] = round(fill_price + (atr * 2), 2)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.active_trade_risk = None

    def next(self):
        if self.order:
            return

        if len(self.datas[0]) < 50:
            return

        # Get last 50 bars
        closes = list(self.datas[0].close.get(size=50))
        highs = list(self.datas[0].high.get(size=50))
        lows = list(self.datas[0].low.get(size=50))
        opens = list(self.datas[0].open.get(size=50))
        volumes = list(self.datas[0].volume.get(size=50))
        timestamps = [bt.num2date(self.datas[0].datetime[-i]) for i in range(50, 0, -1)]  # oldest to newest

        df = pd.DataFrame({
            'timestamp': timestamps,
            'open': opens,
            'high': highs,
            'low': lows,
            'close': closes,
            'volume': volumes
        })
        df.set_index('timestamp', inplace=True)
        df['returns'] = (df['close'] / df['close'].shift(1) - 1)  # Simple returns for backtrader

        metrics = calculate_metrics(df)
        if not metrics:
            return

        tags, _ = classify_market(metrics, df)

        position_ctx = None
        if self.position:
            price = metrics['last_close']
            position_ctx = {
                'quantity': int(self.position.size),
                'stop_loss': self.active_trade_risk.get('stop_loss') if self.active_trade_risk else None,
                'target_price': self.active_trade_risk.get('target_price') if self.active_trade_risk else None,
                'entry_price': self.position.price,
                'current_price': price,
            }

        signal = evaluate_strategy(
            symbol=self.data._name or 'BACKTEST',
            metrics=metrics,
            tags=tags,
            context={
                'position': position_ctx,
                'cash_available': self.broker.getcash(),
                'now': datetime.utcnow(),
            },
        )

        if not signal:
            return

        if signal.action == 'open' and not self.position and signal.quantity:
            self.active_trade_risk = {
                'stop_loss': signal.stop_loss,
                'target_price': signal.target_price,
                'atr': metrics.get('atr') or 0,
            }
            self.order = self.buy(size=int(signal.quantity))
        elif signal.action == 'close' and self.position:
            self.order = self.sell(size=int(self.position.size))
            self.active_trade_risk = None

def run_backtest(symbol):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TradingStrategy)

    # Fetch historical data
    df = get_historical_data(symbol, days=BACKTEST_DAYS)
    if df.empty:
        print(f"No data for backtest on {symbol}")
        return

    # Convert to backtrader format
    data = bt.feeds.PandasData(dataname=df[['open', 'high', 'low', 'close', 'volume']])

    cerebro.adddata(data)
    cerebro.broker.setcash(10000.0)  # Starting cash
    cerebro.broker.setcommission(commission=0.001)  # 0.1% commission

    print(f'Starting Portfolio Value: {cerebro.broker.getvalue():.2f}')
    cerebro.run()
    print(f'Final Portfolio Value: {cerebro.broker.getvalue():.2f}')

    # Plot results (if matplotlib available)
    try:
        cerebro.plot()
    except:
        pass