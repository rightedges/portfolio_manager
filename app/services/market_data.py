import requests
import yfinance as yf
from flask_login import current_user
from datetime import datetime

BASE_URL = "https://api.twelvedata.com"

def get_api_key():
    if current_user.is_authenticated and current_user.api_key:
        return current_user.api_key
    return None

def check_symbol(symbol):
    """
    Verifies if a stock symbol is available on Twelve Data or Yahoo Finance.
    Returns True if valid, False otherwise.
    """
    # 1. Try Twelve Data if API key is present
    api_key = get_api_key()
    if api_key:
        url = f"{BASE_URL}/quote"
        params = {
            "symbol": symbol,
            "apikey": api_key
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()
            if "code" not in data or data["code"] == 200:
                return True
        except Exception as e:
            print(f"Twelve Data check failed: {e}")

    # 2. Fallback to Yahoo Finance
    try:
        ticker = yf.Ticker(symbol)
        # Try fetching 1 day of history to verify existence
        hist = ticker.history(period="1d")
        if not hist.empty:
            return True
        # If history is empty, it likely doesn't exist
        return False
    except Exception as e:
        print(f"Yahoo Finance check failed: {e}")
        # If we hit a rate limit or other error, we can't verify.
        # Better to allow it than block valid symbols due to API limits.
        # The user will just see 0 price if it's truly invalid.
        return True

def get_yahoo_price(symbol):
    try:
        ticker = yf.Ticker(symbol)
        # Get latest data
        # history(period='1d') returns a DataFrame
        hist = ticker.history(period="1d")
        if not hist.empty:
            price = float(hist['Close'].iloc[-1])
            # Timestamp from the index (Date)
            timestamp = hist.index[-1].strftime('%Y-%m-%d %H:%M:%S')
            return {'price': price, 'timestamp': timestamp}
    except Exception as e:
        print(f"Error fetching Yahoo price for {symbol}: {e}")
    return None

def get_prices(symbols):
    """
    Fetches prices for multiple symbols.
    Tries Twelve Data first, then falls back to Yahoo Finance for any missing/failed symbols.
    """
    results = {}
    remaining_symbols = list(symbols)
    
    # 1. Try Twelve Data
    api_key = get_api_key()
    if api_key and remaining_symbols:
        symbol_str = ",".join(remaining_symbols)
        url = f"{BASE_URL}/quote"
        params = {
            "symbol": symbol_str,
            "apikey": api_key
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            # Helper to process single item
            def process_item(sym, item):
                if "close" in item:
                    return {
                        'price': float(item["close"]),
                        'timestamp': item.get("datetime", "")
                    }
                return None

            if len(remaining_symbols) == 1:
                # Single symbol response is a dict
                res = process_item(remaining_symbols[0], data)
                if res:
                    results[remaining_symbols[0]] = res
                    remaining_symbols.remove(remaining_symbols[0])
            else:
                # Multiple symbols response is dict of dicts
                for sym in list(remaining_symbols): # Copy to iterate safely
                    if sym in data:
                        res = process_item(sym, data[sym])
                        if res:
                            results[sym] = res
                            remaining_symbols.remove(sym)
                            
        except Exception as e:
            print(f"Twelve Data fetch failed: {e}")

    # 2. Fallback to Yahoo Finance for remaining symbols
    for sym in remaining_symbols:
        res = get_yahoo_price(sym)
        if res:
            results[sym] = res
            
    return results
