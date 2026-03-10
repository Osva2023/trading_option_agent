import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import DATABASE_URI

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(PROJECT_ROOT, 'web', 'templates')
STATIC_DIR = os.path.join(PROJECT_ROOT, 'web', 'static')

# Database setup
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class MarketData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    close_price = db.Column(db.Float)
    volume = db.Column(db.Integer)
    volatility = db.Column(db.Float)
    atr = db.Column(db.Float)
    ema20 = db.Column(db.Float)
    ema50 = db.Column(db.Float)
    ema200 = db.Column(db.Float)
    rsi = db.Column(db.Float)
    tags = db.Column(db.String(200))

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    alert_type = db.Column(db.String(50))
    message = db.Column(db.Text)

class OptionsData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    spot_price = db.Column(db.Float)
    calls_count = db.Column(db.Integer)
    puts_count = db.Column(db.Integer)
    avg_call_iv = db.Column(db.Float)
    avg_put_iv = db.Column(db.Float)
    nearest_expiration = db.Column(db.String(20))

class PaperPosition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False, unique=True)
    strategy = db.Column(db.String(50), nullable=False)
    entry_time = db.Column(db.DateTime, default=datetime.utcnow)
    entry_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    stop_loss = db.Column(db.Float)
    target_price = db.Column(db.Float)
    current_price = db.Column(db.Float)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    entry_reason = db.Column(db.Text)

class PaperTrade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    strategy = db.Column(db.String(50), nullable=False)
    entry_time = db.Column(db.DateTime, nullable=False)
    exit_time = db.Column(db.DateTime, default=datetime.utcnow)
    entry_price = db.Column(db.Float, nullable=False)
    exit_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    realized_pnl = db.Column(db.Float, nullable=False)
    realized_pct = db.Column(db.Float, nullable=False)
    entry_reason = db.Column(db.Text)
    exit_reason = db.Column(db.Text)

# Create tables
with app.app_context():
    db.create_all()

def save_market_data(symbol, metrics, tags):
    """Save market metrics to database."""
    try:
        with app.app_context():
            data = MarketData(
                symbol=symbol,
                close_price=metrics['last_close'],
                volume=0,  # Not available in metrics, could add
                volatility=metrics['current_vol'],
                atr=metrics['atr'],
                ema20=metrics['ema20'],
                ema50=metrics['ema50'],
                ema200=metrics['ema200'],
                rsi=metrics.get('rsi'),
                tags=', '.join(tags)
            )
            db.session.add(data)
            db.session.commit()
    except Exception as e:
        print(f"Failed to save market data for {symbol}: {str(e)}")

def save_alert(symbol, alert_type, message):
    """Save alert to database."""
    try:
        with app.app_context():
            alert = Alert(symbol=symbol, alert_type=alert_type, message=message)
            db.session.add(alert)
            db.session.commit()
    except Exception as e:
        print(f"Failed to save alert for {symbol}: {str(e)}")

def save_options_data(symbol, options_info):
    """Save options data to database."""
    if not options_info:
        return
    try:
        with app.app_context():
            data = OptionsData(
                symbol=symbol,
                spot_price=options_info['spot_price'],
                calls_count=options_info['calls_count'],
                puts_count=options_info['puts_count'],
                avg_call_iv=options_info['avg_call_iv'],
                avg_put_iv=options_info['avg_put_iv'],
                nearest_expiration=str(options_info['nearest_expiration'])
            )
            db.session.add(data)
            db.session.commit()
    except Exception as e:
        print(f"Failed to save options data for {symbol}: {str(e)}")

def get_open_paper_position(symbol):
    """Return the open paper position for a symbol, if any."""
    with app.app_context():
        return PaperPosition.query.filter_by(symbol=symbol).first()

def list_open_paper_positions():
    """Return all open paper positions."""
    with app.app_context():
        return PaperPosition.query.order_by(PaperPosition.entry_time.asc()).all()

def list_recent_paper_trades(limit=20):
    """Return the most recent closed paper trades."""
    with app.app_context():
        return PaperTrade.query.order_by(PaperTrade.exit_time.desc()).limit(limit).all()

def open_paper_position(symbol, strategy, entry_price, quantity, stop_loss=None, target_price=None, entry_reason=''):
    """Open a new paper position for a symbol."""
    try:
        with app.app_context():
            existing = PaperPosition.query.filter_by(symbol=symbol).first()
            if existing:
                return existing

            position = PaperPosition(
                symbol=symbol,
                strategy=strategy,
                entry_price=entry_price,
                quantity=quantity,
                stop_loss=stop_loss,
                target_price=target_price,
                current_price=entry_price,
                entry_reason=entry_reason,
            )
            db.session.add(position)
            db.session.commit()
            return position
    except Exception as e:
        print(f"Failed to open paper position for {symbol}: {str(e)}")
        return None

def update_paper_position_price(symbol, current_price):
    """Update the mark price for an existing paper position."""
    try:
        with app.app_context():
            position = PaperPosition.query.filter_by(symbol=symbol).first()
            if not position:
                return None

            position.current_price = current_price
            position.last_updated = datetime.utcnow()
            db.session.commit()
            return position
    except Exception as e:
        print(f"Failed to update paper position for {symbol}: {str(e)}")
        return None

def close_paper_position(symbol, exit_price, exit_reason):
    """Close an open paper position and record a paper trade."""
    try:
        with app.app_context():
            position = PaperPosition.query.filter_by(symbol=symbol).first()
            if not position:
                return None

            realized_pnl = (exit_price - position.entry_price) * position.quantity
            realized_pct = ((exit_price / position.entry_price) - 1) * 100 if position.entry_price else 0

            trade = PaperTrade(
                symbol=position.symbol,
                strategy=position.strategy,
                entry_time=position.entry_time,
                exit_price=exit_price,
                entry_price=position.entry_price,
                quantity=position.quantity,
                realized_pnl=realized_pnl,
                realized_pct=realized_pct,
                entry_reason=position.entry_reason,
                exit_reason=exit_reason,
            )
            db.session.add(trade)
            db.session.delete(position)
            db.session.commit()
            return trade
    except Exception as e:
        print(f"Failed to close paper position for {symbol}: {str(e)}")
        return None

def get_paper_account_summary(starting_cash):
    """Compute paper account summary from open positions and closed trades."""
    with app.app_context():
        positions = PaperPosition.query.all()
        trades = PaperTrade.query.all()

        realized_pnl = sum(trade.realized_pnl for trade in trades)
        committed_capital = sum(position.entry_price * position.quantity for position in positions)
        market_value = sum((position.current_price or position.entry_price) * position.quantity for position in positions)
        unrealized_pnl = sum(((position.current_price or position.entry_price) - position.entry_price) * position.quantity for position in positions)
        cash = starting_cash + realized_pnl - committed_capital

        return {
            'starting_cash': round(starting_cash, 2),
            'cash': round(cash, 2),
            'committed_capital': round(committed_capital, 2),
            'market_value': round(market_value, 2),
            'realized_pnl': round(realized_pnl, 2),
            'unrealized_pnl': round(unrealized_pnl, 2),
            'equity': round(cash + market_value, 2),
            'open_positions': len(positions),
            'closed_trades': len(trades),
        }