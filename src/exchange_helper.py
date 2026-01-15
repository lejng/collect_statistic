import pandas as pd
from ccxt import Exchange

# Get history candles
def get_ohlcv(exchange: Exchange, symbol, timeframe='1h', limit=500) -> pd.DataFrame:
    try:
        data = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    except Exception as e:
        print(f"Error during getting data {symbol}: {e}")
        return pd.DataFrame()
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df.set_index('timestamp')

def get_symbols_spot(exchange: Exchange) -> list[str]:
    markets = exchange.load_markets()
    all_symbols = [
        market['symbol']
        for market in markets.values()
        if market.get('active')
           and market.get('quote') in ['USDT', 'BUSD', 'FDUSD', 'USD', 'USDC']
           and market.get('type', '') == 'spot'
    ]
    return all_symbols

def get_symbols_swap(exchange: Exchange) -> list[str]:
    markets = exchange.load_markets()
    all_symbols = [
        market['symbol']
        for market in markets.values()
        if market.get('active')
           and market.get('quote') in ['USDT', 'BUSD', 'FDUSD', 'USD', 'USDC']
           and market.get('type', '') == 'swap'
    ]
    return all_symbols

def get_symbols_futures(exchange: Exchange) -> list[str]:
    markets = exchange.load_markets()
    all_symbols = [
        market['symbol']
        for market in markets.values()
        if market.get('active')
           and market.get('quote') in ['USDT', 'BUSD', 'FDUSD', 'USD', 'USDC']
           and market.get('type', '') == 'future'
    ]
    return all_symbols