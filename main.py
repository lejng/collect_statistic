# This is a sample Python script.
import multiprocessing
import time

from src.arb_future_bot_collector import monitor

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


if __name__ == "__main__":
    trading_pairs_list = [
        ('BTC/USDT', 'BTC/USDT:USDT-260925'),
        ('BTC/USDT', 'BTC/USDT:USDT-260626'),
        ('BTC/USDT', 'BTC/USDT:USDT-260327'),
        ('BTC/USDT:USDT-260327', 'BTC/USDT:USDT-260626'),
        ('BTC/USDT:USDT-260327', 'BTC/USDT:USDT-260925'),
        ('BTC/USDT:USDT-260327', 'BTC/USDT:USDT-261225'),
        ('ETH/USDT', 'ETH/USDT:USDT-261225'),
        ('ETH/USDT', 'ETH/USDT:USDT-260626'),
        ('ETH/USDT', 'ETH/USDT:USDT-260327'),
        ('ETH/USDT:USDT-260327', 'ETH/USDT:USDT-261225'),
        ('ETH/USDT:USDT-260327', 'ETH/USDT:USDT-260626'),
        ('MNT/USDT', 'MNT/USDT:USDT-260227'),
        ('MNT/USDT:USDT-260123', 'MNT/USDT:USDT-260227'),
        ('SOL/USDT', 'SOL/USDT:USDT-260227'),
        ('SOL/USDT:USDT-260123', 'SOL/USDT:USDT-260227'),
        ('XRP/USDT', 'XRP/USDT:USDT-260227'),
        ('XRP/USDT:USDT-260123', 'XRP/USDT:USDT-260227'),
        ('DOGE/USDT', 'DOGE/USDT:USDT-260227'),
        ('DOGE/USDT:USDT-260123', 'DOGE/USDT:USDT-260227')
    ]
    processes = []
    for spot_pair, future_pair in trading_pairs_list:
        p = multiprocessing.Process(
            target=monitor,
            args=(future_pair, spot_pair),
            # this solution only for collect data, for bot better use one thread for start
            daemon=True
        )
        p.start()
        processes.append(p)

    try:
        # Основной процесс должен просто висеть и ничего не делать,
        # пока вы не решите остановить программу
        while True:
            print("Collecting statistic...")
            time.sleep(10)
    except KeyboardInterrupt:
        print("End script...")
        # Все даэмоны умрут сами в этой точке
