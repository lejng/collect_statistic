import pandas as pd
import matplotlib.pyplot as plt

# Укажи имя своего файла
filename = "/Users/leo/python_projects/collect_statistic/BTC_USDT_USDT_260626_and_BTC_USDT_arbitrage_monitor_1768504300817990000.csv"
df_log = pd.read_csv(filename, parse_dates=['timestamp'])

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

# График спреда
ax1.plot(df_log['timestamp'], df_log['current_spread'], label='Current Spread')
ax1.plot(df_log['timestamp'], df_log['mean_spread'], label='Mean Spread', linestyle='--')
ax1.set_title('Spread Analysis')
ax1.legend()

# График Z-Score
ax2.plot(df_log['timestamp'], df_log['zscore'], color='orange', label='Z-Score')
ax2.axhline(y=2, color='r', linestyle='--', alpha=0.5)
ax2.axhline(y=-2, color='r', linestyle='--', alpha=0.5)
ax2.set_title('Z-Score Analysis')
ax2.legend()

plt.show()