"""
1. pip3 install ccxt
2. pip3 install backtrader
Of course, we said that the reason for choosing the backtrader is that it integrates ccxt.
But the official version is not integrated with ccxt.
But on the branch:https://github.com/bartosh/backtrader/tree/ccxt
Therefore, we have to install it by:
3. ОБЯЗАТЕЛЬНО Сохранить файл /plot/locator.py в библиотеке backtrader
4. pip install --upgrade git+https://github.com/bartosh/backtrader.git@ccxt
5. Файл /plot/locator.py в библиотеке backtrader - на 2024.05.28 - содержит ошибку и не дает возможность печатать графики (конфликт с функ. warning)
На всякий случай можно его тоже сохранить перед перезаписью
6. Файл /plot/locator.py - восстановить из исходного
"""

# from __future__ import(absolute_import, division, print_function, unicode_literals)
from datetime import datetime, timedelta
import backtrader as bt
from backtrader import cerebro
import time

def connect_broker():
    """
    это просто функция, которая подключается к бирже и не вызывается в приведенном выше коде.
    На самом деле это всего лишь несколько строк кода:
    """
    config = {'urls': {'api': 'https://api.sandbox.gemini.com'},
                         'apiKey': 'XXXXX',
                         'secret': 'XXXXX',
                         'nonce': lambda: str(int(time.time() * 1000))
                        }
    broker = bt.brokers.CCXTBroker(exchange='gemini',
                                   currency='USDT', config=config)
    cerebro.setbroker(broker)

    # Create data feeds
    data_ticks = bt.feeds.CCXT(exchange='geminy', symbol='BTC/USDT',
                              name="btc_usdt_tick",
                              timeframe=bt.TimeFrame.Ticks,
                              compression=1, config=config)
    cerebro.adddata(data_ticks)


class TestStrategy(bt.Strategy):
    def next(self):
        print('NEXT: |',
              bt.num2date(self.data.datetime[0]), '|',
              self.data._name,     '|',
              self.data.open[0],   '|',
              self.data.high[0],   '|',
              self.data.low[0],    '|',
              self.data.close[0],  '|',
              self.data.volume[0], '|',
              bt.TimeFrame.getname(self.data._timeframe), len(self.data))
        # print(self.data.lines.__dict__)

if __name__ == '__main__':
    cerebro = bt.Cerebro()

    # hist_start_date = datetime.utcnow() - timedelta(minutes=5)
    hist_start_date = datetime.utcnow() - timedelta(minutes=5)
    data_min = bt.feeds.CCXT(exchange='bitteam', # 'bitmex'
                             symbol="DUSD/USDT",
                             name="DUSD/USDT_1min",
                             fromdate=hist_start_date,
                             timeframe=bt.TimeFrame.Minutes) # bt.TimeFrame.Days
    cerebro.adddata(data_min)
    cerebro.addstrategy(TestStrategy)
    cerebro.run()