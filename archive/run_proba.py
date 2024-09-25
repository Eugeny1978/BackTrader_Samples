import backtrader as bt
from datetime import datetime


class MyStrategy(bt.Strategy):
    def __init__(self):
        self.order = None  # Для хранения текущего ордера

    def next(self):
        # Проверяем, есть ли текущий ордер
        if self.order:
            return  # Если ордер открыт, ничего не делаем

        # Получаем информацию о текущей позиции
        if self.position:  # Если у нас есть открытая позиция
            # Закрываем текущую позицию
            self.order = self.close()  # Закрываем позицию
            self.log('Закрываем позицию: {}'.format(self.position.size))

        else:  # Если позиции нет, открываем новую
            # Например, открываем новую длинную позицию
            self.order = self.buy(size=1)  # Открываем новую длинную позицию
            self.log('Открываем новую длинную позицию')

    def log(self, text):
        # Функция для вывода информации в лог
        dt = self.data.datetime.date(0)
        print(f'{dt.isoformat()} {text}')


# Создаем экземпляр Cerebro
cerebro = bt.Cerebro()

# Загружаем данные
data = bt.feeds.YahooFinanceData(dataname='AAPL', fromdate=datetime(2022, 1, 1),
                                 todate=datetime(2022, 12, 31))
cerebro.adddata(data)

# Добавляем стратегию
cerebro.addstrategy(MyStrategy)

# Запускаем
cerebro.run()