import pandas as pd
import matplotlib.pyplot as plt

import glob
import os

from matplotlib.ticker import ScalarFormatter

# Путь к твоей папке с данными
path = "/Users/leo/python_projects/collect_statistic/data/"
# Ищем все CSV файлы монитора
all_files = glob.glob(os.path.join(path, "*_arbitrage_monitor_*.csv"))

"""
all_files = [
    path + 'ETH_USDT_USDT_260626_and_ETH_USDT_arbitrage_monitor_1768506427631274507.csv'
]
"""

print(all_files)
if not all_files:
    print("Файлы не найдены!")
else:
    for filename in all_files:
        # Читаем данные
        df_log = pd.read_csv(filename, parse_dates=['timestamp'])

        # Вырезаем красивое имя из названия файла для заголовка окна
        title_name = os.path.basename(filename).split('_arbitrage')[0]

        # Создаем НОВУЮ фигуру для каждого файла
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
        fig.canvas.manager.set_window_title(f"Arbitrage Monitor: {title_name}")

        # 1. Верхний график: Спред
        print(df_log['current_spread'])
        ax1.plot(df_log['timestamp'], df_log['current_spread'], label='Current Spread', color='#1f77b4')
        ax1.plot(df_log['timestamp'], df_log['mean_spread'], label='Mean Spread', linestyle='--', color='black',
                 alpha=0.6)
        # ПРИНУДИТЕЛЬНО ВЫКЛЮЧАЕМ СМЕЩЕНИЕ:
        y_formatter = ScalarFormatter(useOffset=False)
        ax1.yaxis.set_major_formatter(y_formatter)
        ax1.set_title(f'Spread Analysis - {title_name}', fontsize=14)
        ax1.set_ylabel('Spread Value')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # 2. Нижний график: Z-Score
        ax2.plot(df_log['timestamp'], df_log['zscore'], color='orange', label='Z-Score')
        ax2.axhline(y=2, color='red', linestyle='--', alpha=0.5, label='Entry Threshold (+2)')
        ax2.axhline(y=-2, color='red', linestyle='--', alpha=0.5, label='Entry Threshold (-2)')
        ax2.axhline(y=0, color='gray', linestyle='-', alpha=0.3)  # Осевая линия (Mean)
        ax2.set_title(f'Z-Score Analysis - {title_name}', fontsize=14)
        ax2.set_ylabel('Z-Score')
        ax2.set_xlabel('Timestamp')
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        plt.tight_layout()

        # Показываем все окна разом (код остановится здесь, пока ты не закроешь окна)
    plt.show()