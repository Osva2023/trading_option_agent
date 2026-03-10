import os
import sys
from flask import Flask, jsonify, render_template
import threading

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import app as flask_app, db, MarketData, Alert, OptionsData
from config.settings import SYMBOLS, FLASK_HOST, FLASK_PORT

# Flask routes for web dashboard
@flask_app.route('/')
def dashboard():
    with flask_app.app_context():
        # Get latest data for each symbol
        latest_data = {}
        for symbol in SYMBOLS:
            data = MarketData.query.filter_by(symbol=symbol).order_by(MarketData.timestamp.desc()).first()
            options = OptionsData.query.filter_by(symbol=symbol).order_by(OptionsData.timestamp.desc()).first()
            alerts = Alert.query.filter_by(symbol=symbol).order_by(Alert.timestamp.desc()).limit(5).all()
            latest_data[symbol] = {
                'market_data': data,
                'options_data': options,
                'recent_alerts': alerts
            }
    return render_template('dashboard.html', data=latest_data)

@flask_app.route('/api/data')
def api_data():
    with flask_app.app_context():
        data = MarketData.query.order_by(MarketData.timestamp.desc()).limit(100).all()
        result = [{
            'symbol': d.symbol,
            'timestamp': d.timestamp.isoformat(),
            'close_price': d.close_price,
            'volatility': d.volatility,
            'tags': d.tags
        } for d in data]
    return jsonify(result)

def start_flask():
    from config.settings import FLASK_HOST
    # Try port 5001 first, then fall back to 5002, 5003, etc.
    for port in range(5001, 5010):
        try:
            print(f"Starting Flask on {FLASK_HOST}:{port}")
            flask_app.run(host=FLASK_HOST, port=port, debug=False, use_reloader=False)
            return
        except OSError as e:
            if port < 5009:
                print(f"Port {port} in use, trying {port+1}...")
                continue
            else:
                print(f"All ports 5001-5009 are in use. Flask dashboard unavailable. Error: {e}")
                return

# Start Flask in background thread
flask_thread = threading.Thread(target=start_flask, daemon=True)
flask_thread.start()

if __name__ == '__main__':
    start_flask()