import numpy as np
import pandas as pd


def calculate_log_returns(prices: pd.Series) -> pd.Series:
    """
    Calculate logarithmic returns from price series.
    Formula: r_t = ln(P_t / P_{t-1}) = ln(P_t) - ln(P_{t-1})
    """
    price_ratio = prices / prices.shift(1)
    log_returns = np.log(price_ratio)
    clean_returns = log_returns.dropna()
    return clean_returns

def get_aligned_price_data(symbol_1_ohlcv, symbol_2_ohlcv) -> tuple | None:
    symbol_1_suffix = '_symbol_1'
    symbol_2_suffix = '_symbol_2'
    merged = pd.merge(
        symbol_1_ohlcv[['timestamp', 'close']],
        symbol_2_ohlcv[['timestamp', 'close']],
        on='timestamp',
        suffixes=(symbol_1_suffix, symbol_2_suffix)
    )
    if len(merged) < 30:
        return None
    symbol_1_close = merged[f'close{symbol_1_suffix}']
    symbol_2_close = merged[f'close{symbol_2_suffix}']
    timestamps = merged['timestamp']
    return symbol_1_close, symbol_2_close, timestamps

def get_aligned_price_data_frame(symbol_1, symbol_1_ohlcv, symbol_2, symbol_2_ohlcv) -> pd.DataFrame:
    # Устанавливаем timestamp как индекс
    symbol_1_indexed = symbol_1_ohlcv.set_index('timestamp')
    symbol_2_indexed = symbol_2_ohlcv.set_index('timestamp')

    # Но лучше переиндексировать по всем уникальным timestamps
    all_timestamps = symbol_1_indexed.index.union(symbol_2_indexed.index)
    merged = pd.concat([
        symbol_1_indexed.reindex(all_timestamps),
        symbol_2_indexed.reindex(all_timestamps)
    ], axis=1, keys=[symbol_1, symbol_2])
    return merged