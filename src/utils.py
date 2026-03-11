import os
import sys
import time
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from polygon import RESTClient
from alpha_vantage.timeseries import TimeSeries
import logging
import yfinance as yf

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (
    POLYGON_API_KEY, ALPHA_VANTAGE_KEY, EMAIL_FROM, EMAIL_TO, EMAIL_PASS,
    SYMBOLS, POLL_INTERVAL, LOG_FILE
)

# Initialize clients
client = RESTClient(POLYGON_API_KEY)

def setup_logging():
    """Setup logging configuration."""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(message)s')

def get_historical_data(symbol, days=5):
    """Fetch intraday bars (15-minute) for the last `days` days."""
    end = datetime.now()
    start = end - timedelta(days=days)
    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')

    # Primary: Polygon 15-minute bars
    try:
        bars = client.get_aggs(
            symbol,
            multiplier=15,
            timespan='minute',
            from_=start_str,
            to=end_str,
            adjusted=True,
            limit=50000  # máximo permitido, cubre varios días
        )
        if not bars:
            raise ValueError("No bars from Polygon")

        df = pd.DataFrame(bars)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df['returns'] = np.log(df['close'] / df['close'].shift(1))
        logging.info(f"Datos intradiarios OK para {symbol}: {len(df)} barras de 15 min")
        return df

    except Exception as e:
        logging.warning(f"Polygon intradiario falló para {symbol}: {str(e)}")

    # Fallback: Alpha Vantage (daily only, no free intraday)
    try:
        ts = TimeSeries(key=ALPHA_VANTAGE_KEY, output_format='pandas')
        df, _ = ts.get_daily_adjusted(symbol, outputsize='full')
        df = df.rename(columns={
            '1. open': 'open', '2. high': 'high', '3. low': 'low',
            '4. close': 'close', '5. adjusted close': 'adjusted_close',
            '6. volume': 'volume', '7. dividend amount': 'dividend',
            '8. split coefficient': 'split'
        })
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df = df[(df.index >= start) & (df.index <= end)]
        df['returns'] = np.log(df['close'] / df['close'].shift(1))
        logging.info(f"Alpha Vantage diario OK para {symbol}: {len(df)} filas")
        return df
    except Exception as e:
        logging.error(f"Alpha Vantage también falló para {symbol}: {str(e)}")

    # Third fallback: Yahoo Finance intraday (15m)
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period='5d', interval='15m')
        if df.empty:
            raise ValueError("No intraday data from Yahoo Finance")
        df.index = pd.to_datetime(df.index)
        df = df.rename(columns={
            'Open': 'open', 'High': 'high', 'Low': 'low',
            'Close': 'close', 'Volume': 'volume'
        })
        df['returns'] = np.log(df['close'] / df['close'].shift(1))
        logging.info(f"Yahoo Finance intradiario OK para {symbol}: {len(df)} filas")
        return df
    except Exception as e:
        logging.warning(f"Yahoo Finance intradiario falló para {symbol}: {str(e)}")

    # Fourth fallback: Yahoo Finance daily
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period='3mo', interval='1d')
        if df.empty:
            raise ValueError("No daily data from Yahoo Finance")
        df.index = pd.to_datetime(df.index)
        df = df.rename(columns={
            'Open': 'open', 'High': 'high', 'Low': 'low',
            'Close': 'close', 'Volume': 'volume'
        })
        df['returns'] = np.log(df['close'] / df['close'].shift(1))
        logging.info(f"Yahoo Finance diario OK para {symbol}: {len(df)} filas")
        return df
    except Exception as e:
        logging.error(f"Yahoo Finance también falló para {symbol}: {str(e)}")
        return pd.DataFrame()

def calculate_rsi(df, period=14):
    """Calculate RSI (Relative Strength Index)"""
    if len(df) < period + 1:
        return None

    # Calculate price changes
    delta = df['close'].diff()

    # Separate gains and losses
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    # Calculate RS (Relative Strength)
    rs = gain / loss

    # Calculate RSI
    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1] if not rsi.empty else None

def calculate_metrics(df):
    if df.empty or len(df) < 50:  # mínimo razonable para intradiario
        return None

    # Volatilidad: 1 hora reciente vs histórico del período
    current_vol = df['returns'][-4:].std() * np.sqrt(252 * 26) * 100   # ~1 hora (4 barras de 15 min)
    hist_vol = df['returns'].std() * np.sqrt(252 * 26) * 100           # anualizado desde barras 15 min

    # ATR: 14 períodos (14 * 15 min = ~3.5 horas)
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    tr = np.maximum(high_low, high_close, low_close)
    atr = tr.rolling(14).mean().iloc[-1]

    # EMAs: ajustadas a intradiario (20/50/200 períodos de 15 min)
    ema20  = df['close'].ewm(span=20, adjust=False).mean().iloc[-1]
    ema50  = df['close'].ewm(span=50, adjust=False).mean().iloc[-1]
    ema200 = df['close'].ewm(span=200, adjust=False).mean().iloc[-1]

    # IV Rank proxy (basado en vol rolling de 30 períodos ~7.5 horas)
    vol_series = df['returns'].rolling(30).std() * np.sqrt(252 * 26) * 100
    iv_rank = 0
    if len(vol_series.dropna()) > 0:
        min_vol = vol_series.min()
        max_vol = vol_series.max()
        if max_vol > min_vol:
            iv_rank = (current_vol - min_vol) / (max_vol - min_vol) * 100

    # RSI: 14 períodos (14 * 15 min = ~3.5 horas)
    rsi = calculate_rsi(df, period=14)

    return {
        'current_vol': round(current_vol, 2),
        'hist_vol': round(hist_vol, 2),
        'iv_rank': round(iv_rank, 1),
        'atr': round(atr, 2),
        'ema20': round(ema20, 2),
        'ema50': round(ema50, 2),
        'ema200': round(ema200, 2),
        'rsi': round(rsi, 2) if rsi is not None else None,
        'last_close': round(df['close'].iloc[-1], 2)
    }

def classify_market(metrics, df):
    if not metrics:
        return [], "No data available"

    tags = []
    advice = []

    # Trend
    if metrics['ema20'] > metrics['ema50'] > metrics['ema200']:
        tags.append('TRENDING_UP')
        advice.append('Bullish trend (EMA stack up).')
    elif metrics['ema20'] < metrics['ema50'] < metrics['ema200']:
        tags.append('TRENDING_DOWN')
        advice.append('Bearish trend (EMA stack down).')

    # Range-bound check (rough)
    price = metrics['last_close']
    if metrics['atr'] < price * 0.012:  # ATR < ~1.2% of price
        tags.append('RANGE_BOUND')
        advice.append('Appears range-bound. Good for neutral strategies.')

    # Volatility
    if metrics['current_vol'] > 1.5 * metrics['hist_vol'] or metrics['iv_rank'] > 70:
        tags.append('HIGH_VOL')
        advice.append('High volatility regime. Avoid selling narrow spreads.')
    elif metrics['iv_rank'] < 30:
        tags.append('LOW_VOL')
        advice.append('Low volatility. Premium selling may be attractive.')

    # RSI (Relative Strength Index)
    if metrics.get('rsi') is not None:
        rsi_value = metrics['rsi']
        if rsi_value > 70:
            tags.append('OVERBOUGHT')
            advice.append(f'RSI {rsi_value:.1f}: Overbought conditions. Potential reversal.')
        elif rsi_value < 30:
            tags.append('OVERSOLD')
            advice.append(f'RSI {rsi_value:.1f}: Oversold conditions. Potential bounce.')
        else:
            tags.append('RSI_NEUTRAL')
            advice.append(f'RSI {rsi_value:.1f}: Neutral momentum.')

    return tags, ' '.join(advice)

def get_options_data(symbol, expiration_date=None):
    """Fetch options chain data for a symbol using Yahoo Finance."""
    try:
        ticker = yf.Ticker(symbol)
        if expiration_date:
            options = ticker.option_chain(expiration_date)
        else:
            # Get nearest expiration
            expirations = ticker.options
            if not expirations:
                logging.warning(f"No options available for {symbol}")
                return None
            options = ticker.option_chain(expirations[0])

        calls = options.calls
        puts = options.puts

        # Basic analysis: Find ATM call/put, implied volatility, etc.
        spot_price = ticker.info.get('regularMarketPrice', ticker.history(period='1d').iloc[-1]['Close'])
        atm_calls = calls[(calls['strike'] >= spot_price * 0.95) & (calls['strike'] <= spot_price * 1.05)]
        atm_puts = puts[(puts['strike'] >= spot_price * 0.95) & (puts['strike'] <= spot_price * 1.05)]

        options_summary = {
            'symbol': symbol,
            'spot_price': spot_price,
            'calls_count': len(calls),
            'puts_count': len(puts),
            'avg_call_iv': atm_calls['impliedVolatility'].mean() if not atm_calls.empty else None,
            'avg_put_iv': atm_puts['impliedVolatility'].mean() if not atm_puts.empty else None,
            'nearest_expiration': expirations[0] if expirations else None
        }

        logging.info(f"Options data fetched for {symbol}: {options_summary}")
        return options_summary

    except Exception as e:
        logging.error(f"Failed to fetch options for {symbol}: {str(e)}")
        return None

def send_email(subject, body):
    # Clean bad chars
    body = body.replace('\xa0', ' ').replace('\u200b', '').replace('\ufeff', '')
    subject = subject.replace('\xa0', ' ').replace('\u200b', '').replace('\ufeff', '')

    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_FROM, EMAIL_PASS)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        logging.info("Email alert sent successfully")
    except Exception as e:
        logging.error(f"Email failed: {str(e)}")

# Market schedule (ET): opening 9:30-10:30, midday 12:00-13:00, before close 15:00-16:00
MARKET_WINDOWS = [
    (9, 30, 10, 30),  # opening
    (12, 0, 13, 0),   # midday
    (15, 0, 16, 0)    # before close
]

def is_market_open(now):
    """Check if current time is within market windows on weekdays."""
    if now.weekday() >= 5:  # weekend
        return False
    hour = now.hour
    minute = now.minute
    for start_h, start_m, end_h, end_m in MARKET_WINDOWS:
        if (hour > start_h or (hour == start_h and minute >= start_m)) and \
           (hour < end_h or (hour == end_h and minute < end_m)):
            return True
    return False

def sleep_until_next_window(now):
    """Calculate seconds to sleep until next market window."""
    if now.weekday() < 5:  # weekday
        for start_h, start_m, _, _ in MARKET_WINDOWS:
            next_time = now.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
            if next_time > now:
                return (next_time - now).total_seconds()
        # next day
        next_day = now + timedelta(days=1)
        while next_day.weekday() >= 5:
            next_day += timedelta(days=1)
        next_time = next_day.replace(hour=9, minute=30, second=0, microsecond=0)
        return (next_time - now).total_seconds()
    else:
        # weekend, sleep to Monday 9:30
        days_to_monday = (7 - now.weekday()) % 7
        if days_to_monday == 0:
            days_to_monday = 7
        next_monday = now + timedelta(days=days_to_monday)
        next_time = next_monday.replace(hour=9, minute=30, second=0, microsecond=0)
        return (next_time - now).total_seconds()