import ccxt

from src.exchange_helper import get_symbols_spot, get_symbols_swap, get_symbols_futures

current_exchange = ccxt.bybit()

print(f"spot tickers: {get_symbols_spot(current_exchange)}")
print(f"swap tickers: {get_symbols_swap(current_exchange)}")
print(f"future tickers:")
for symbol in get_symbols_futures(current_exchange):
    print(symbol)