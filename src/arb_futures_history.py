import ccxt
import pandas as pd
from matplotlib import pyplot as plt

from src.exchange_helper import get_ohlcv

DEFAULT_TIMEFRAME = "1h"
DEFAULT_OHLCV_LIMIT = 2000
ENTRY_Z = 2.0
EXIT_Z = 0.5
WINDOW = 60
PERCENTS = 0.7

exchange = ccxt.bybit()
#exchange = ccxt.gateio()
symbol_future = 'XRP/USDT:USDT-260116'#'ETH/USDT:USDT-260925'#'BTC/USDT:USDT-260925' 'ETH/USDT:USDT-260925'
symbol_spot = 'XRP/USDT'#'ETH/USDC'#'WBTC/USDT'
#symbol_spot = 'BTC/USDT'
#symbol_2 = 'BTC/USDT:USDT-260130'

future_ohlcv = get_ohlcv(exchange, symbol_future, DEFAULT_TIMEFRAME, DEFAULT_OHLCV_LIMIT)
spot_ohlcv = get_ohlcv(exchange, symbol_spot, DEFAULT_TIMEFRAME, DEFAULT_OHLCV_LIMIT)

df = pd.DataFrame({
    symbol_future: future_ohlcv['close'],
    symbol_spot: spot_ohlcv['close']
}).dropna()

df['spread'] = df[symbol_future] / df[symbol_spot] * 100
df['mean'] = df['spread'].rolling(WINDOW).mean()
# standard deviation
df['std'] = df['spread'].rolling(WINDOW).std()
df['zscore'] = (df['spread'] - df['mean']) / df['std']

df['signal'] = 0

# Short symbol_1 / Long symbol_2
df.loc[df['zscore'] > ENTRY_Z, 'signal'] = -1
df.loc[df['spread'] >= df['mean'] + PERCENTS, 'action'] = 'sell future and buy spot'

# Long symbol_1 / Short symbol_2
#df.loc[df['zscore'] < -ENTRY_Z, 'signal'] = 1

# Выход тут нужно будет потом продумать так как выход наступает сразу если з скоре не экстремальный
df.loc[df['zscore'].abs() < EXIT_Z, 'signal'] = 0

print(df.to_string())

plt.figure(figsize=(12,5))
plt.plot(df['spread'], label='Spread')
plt.plot(df['mean'], label='Mean')
plt.plot(df['mean'] + PERCENTS, linestyle='-.', label=f"+{PERCENTS}%")
plt.plot(df['mean'] - PERCENTS, linestyle='-.', label=f"-{PERCENTS}%")
plt.plot(df['mean'] + ENTRY_Z*df['std'], linestyle='--', label=f"+{ENTRY_Z}σ")
plt.plot(df['mean'] - ENTRY_Z*df['std'], linestyle='--', label=f"-{ENTRY_Z}σ")
plt.legend()
plt.title(f"Spread with Mean and ±{ENTRY_Z}σ")
plt.show()

