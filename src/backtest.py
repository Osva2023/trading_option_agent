import os
import sys
import backtrader as bt
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import get_historical_data, calculate_metrics, classify_market
from config.settings import BACKTEST_DAYS

class TradingStrategy(bt.Strategy):
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None

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

        # Simple strategy: Buy on TRENDING_UP + LOW_VOL, Sell on TRENDING_DOWN
        if 'TRENDING_UP' in tags and 'LOW_VOL' in tags and not self.position:
            self.order = self.buy()
        elif 'TRENDING_DOWN' in tags and self.position:
            self.order = self.sell()

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