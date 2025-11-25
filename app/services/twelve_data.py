import requests
from flask_login import current_user

BASE_URL = "https://api.twelvedata.com"

def get_api_key():
    if current_user.is_authenticated and current_user.api_key:
        return current_user.api_key
    return None

def check_symbol(symbol):
    """
    Verifies if a stock symbol is available on Twelve Data.
    Returns True if valid, False otherwise.
    """
    api_key = get_api_key()
    if not api_key:
        return False # Or raise an error indicating missing API key

    # We can use the symbol_search endpoint or just try to fetch a quote.
    # Fetching a quote is often a good enough check and cheaper/simpler if we just want existence.
    # However, symbol_search is more robust for verification.
    # Let's use quote for simplicity and direct verification of data availability.
    
    url = f"{BASE_URL}/quote"
    params = {
        "symbol": symbol,
        "apikey": api_key
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if "code" in data and data["code"] != 200:
            return False
        
        # If we get a valid quote, the symbol exists.
        return True
    except Exception as e:
        print(f"Error checking symbol: {e}")
        return False

def get_price(symbol):
    """
    Fetches the current price for a given symbol.
    Returns the price as a float, or None if failed.
    """
    api_key = get_api_key()
    if not api_key:
        return None

    url = f"{BASE_URL}/price"
    params = {
        "symbol": symbol,
        "apikey": api_key
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if "price" in data:
            return float(data["price"])
        else:
            print(f"Error fetching price for {symbol}: {data}")
            return None
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None

def get_prices(symbols):
    """
    Fetches prices for multiple symbols in one go (if possible, or loop).
    Twelve Data supports batch requests for price endpoint.
    """
    api_key = get_api_key()
    if not api_key:
        return {}
        
    if not symbols:
        return {}

    symbol_str = ",".join(symbols)
    url = f"{BASE_URL}/price"
    params = {
        "symbol": symbol_str,
        "apikey": api_key
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        # If single symbol, response is just the dict. If multiple, it's a dict of dicts.
        if len(symbols) == 1:
             if "price" in data:
                 return {symbols[0]: float(data["price"])}
             return {}
        
        result = {}
        for sym, info in data.items():
            if "price" in info:
                result[sym] = float(info["price"])
        return result

    except Exception as e:
        print(f"Error fetching prices: {e}")
        return {}
