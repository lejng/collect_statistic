import time
from typing import Literal

import ccxt
import pandas as pd
import csv
import os

from src.exchange_helper import get_ohlcv

DEFAULT_TIMEFRAME = "1h"
UPDATE_INTERVAL_IN_SECONDS = 3600
PAUSE_INTERVAL_IN_SECONDS = 60
WINDOW = 60
DEFAULT_OHLCV_LIMIT = WINDOW * 2
POSITION_AMOUNT_FOR_ONE_SIDE = 1000
#standard deviation
PERCENT_DIFFERENT_OPEN = 0.7
PERCENT_DIFFERENT_CLOSE = 0.1
# sum of all commissions buy spot 0.1 sell spot 0.1 buy future 0.055 and sell future 0.055
COMMISSIONS_IN_PERCENTS = 0.31

exchange = ccxt.bybit()

def normalize_name(name: str) -> str:
    return name.replace('/', '_').replace(':', '_').replace('-', '_')

def update_data(symbol_future: str, symbol_spot: str) -> pd.DataFrame:
    future_ohlcv = get_ohlcv(exchange, symbol_future, DEFAULT_TIMEFRAME, DEFAULT_OHLCV_LIMIT)
    spot_ohlcv = get_ohlcv(exchange, symbol_spot, DEFAULT_TIMEFRAME, DEFAULT_OHLCV_LIMIT)

    data_frame = pd.DataFrame({
        symbol_future: future_ohlcv['close'],
        symbol_spot: spot_ohlcv['close']
    }).dropna().shift(1)

    data_frame['spread'] = data_frame[symbol_future] / data_frame[symbol_spot] * 100
    data_frame['mean'] = data_frame['spread'].rolling(WINDOW).mean()
    # standard deviation
    data_frame['std'] = data_frame['spread'].rolling(WINDOW).std()
    data_frame['zscore'] = (data_frame['spread'] - data_frame['mean']) / data_frame['std']
    return data_frame.dropna()

def get_execution_price(symbol: str, side: Literal['buy', 'sell'], amount_usd):
    """Считает среднюю цену исполнения с учетом глубины стакана"""
    try:
        order_book = exchange.fetch_order_book(symbol, limit=100)
        orders = order_book['asks'] if side == 'buy' else order_book['bids']

        total_qty = 0.0
        total_spent = 0.0
        slippage_buffer = 1.2
        amount_usd_adjusted = slippage_buffer * amount_usd

        for price, qty in orders:
            price = float(price)
            qty = float(qty)
            level_vol_usd = price * qty

            needed_usd = amount_usd_adjusted - total_spent

            if level_vol_usd >= needed_usd:
                # Этот уровень полностью закрывает остаток
                fill_qty = needed_usd / price
                total_qty += fill_qty
                total_spent += needed_usd
                return total_spent / total_qty
            else:
                # Забираем весь уровень и идем глубже
                total_qty += qty
                total_spent += level_vol_usd

        return None  # Недостаточно ликвидности в топ-20
    except Exception as e:
        print(f"Error during processing orderbook {symbol}: {e}")
        return None

def log_data(future_price: float, spot_price: float, mean_spread: float, current_spread: float, current_zscore: float):
    delta_spread = current_spread - mean_spread
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | sell future: {future_price:.4f} | buy spot: {spot_price:.4f} | current spread (based orderbook): {current_spread:.4f} | mean spread: {mean_spread:.4f}| delta spread: {delta_spread:.4f} | zscore: {current_zscore:.4f}")

def save_to_csv(data_dict, log_file: str):
    file_exists = os.path.isfile(log_file)
    with open(log_file, mode='a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data_dict.keys())
        if not file_exists:
            writer.writeheader()  # Пишем заголовок только один раз
        writer.writerow(data_dict)

def monitor(symbol_future: str, symbol_spot: str):
    csv_folder_name = 'data'
    if not os.path.exists(csv_folder_name):
        os.makedirs(csv_folder_name)
    log_file = f"{csv_folder_name}/{normalize_name(symbol_future)}_and_{normalize_name(symbol_spot)}_arbitrage_monitor_{time.time_ns()}.csv"
    df = update_data(symbol_future, symbol_spot)
    is_in_position = False
    open_spread = 0.0
    while True:
        try:
            latest_candle_time_seconds = df.index[-1].timestamp()
            current_time_seconds = time.time()
            if current_time_seconds - latest_candle_time_seconds > UPDATE_INTERVAL_IN_SECONDS:
                df = update_data(symbol_future, symbol_spot)
            future_execution_price = get_execution_price(symbol_future, 'sell', POSITION_AMOUNT_FOR_ONE_SIDE)
            spot_execution_price = get_execution_price(symbol_spot, 'buy', POSITION_AMOUNT_FOR_ONE_SIDE)
            if future_execution_price is None or spot_execution_price is None:
                print("Orderbook is thin")
                continue
            current_spread_last = future_execution_price / spot_execution_price * 100
            current_mean_spread = df['mean'].iloc[-1]
            current_zscore = (current_spread_last - current_mean_spread) / df['std'].iloc[-1]
            log_entry = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'future_price': future_execution_price,
                'spot_price': spot_execution_price,
                'current_spread': current_spread_last,
                'mean_spread': current_mean_spread,
                'delta_spread': current_spread_last - current_mean_spread,
                'zscore': current_zscore,
                'is_in_position': int(is_in_position)
            }
            save_to_csv(log_entry, log_file)
            log_data(future_execution_price, spot_execution_price, current_mean_spread, current_spread_last,
                     current_zscore)
            if current_spread_last - current_mean_spread >= PERCENT_DIFFERENT_OPEN and not is_in_position:
                print('===== Open position =====')
                log_data(future_execution_price, spot_execution_price, current_mean_spread, current_spread_last,
                         current_zscore)
                open_spread = current_spread_last
                is_in_position = True
            if current_spread_last - current_mean_spread <= PERCENT_DIFFERENT_CLOSE and is_in_position:
                print('===== Close position =====')
                spread_change_pct = (open_spread - current_spread_last - COMMISSIONS_IN_PERCENTS) / 100
                profit = spread_change_pct * POSITION_AMOUNT_FOR_ONE_SIDE
                log_data(future_execution_price, spot_execution_price, current_mean_spread, current_spread_last,
                         current_zscore)
                print(f"Profit: {profit}")
                is_in_position = False
        except Exception as e:
            print(f"Error in loop: {e}")
        time.sleep(PAUSE_INTERVAL_IN_SECONDS)