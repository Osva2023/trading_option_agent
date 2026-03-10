import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import DATABASE_URI

# Database setup
app = Flask(__name__)
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