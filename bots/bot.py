import datetime
import backtrader as bt
import pandas as pd

from forecast import Forecast
from data_df import load_data


class USDTSizer(bt.Sizer):
    """
    Собственный класс Sizer
    Корректен Только для Пар XXX/USDT
    Чтобы сделать универсальным (и для Кросс-Курсов) нужно брать запрос на котировку
    """
    params = {'usdt': 1000,
              'min_size': 0.00001}
    def __init__(self):
        super().__init__()
        self.decimal = self.count_decimal()

    def _getsizing(self, comminfo, cash, data, isbuy):
        """
        Логика для расчета размера позиции
        # Например, использовать 10% от наличных средств
        size = int(cash * 0.1 / data.close[0])
        """
        size = round(self.params.usdt / data.close[0], self.decimal)
        # Убедимся, что размер не меньше минимавльного
        return max(size, self.params.min_size)

    def count_decimal(self):
        number_str = str(self.params.min_size)
        decimal = 0
        if 'e' in number_str and not '-' in number_str:
            return decimal
        if 'e-' in number_str:
            number_str, degree = number_str.split('e-')
            decimal += int(degree)
        if '.' in number_str:
            integer_part, decimal_part = number_str.split('.')
            decimal_part = decimal_part.rstrip('0')
            decimal += len(decimal_part)
        return decimal


class ForecastStrategy(bt.Strategy):
    columns = ['side', 'open_price', 'close_price', 'size', 'cost', 'pnl', 'commis', 'pnlcomm']

    def log(self, message=None, dt=None):
        """
        Вывод строки с Датой на Консоль
        :param message:
        :param dt:
        """
        dt = dt or self.datas[0].datetime.date() # Заданная Дата или Дата Текущего Бара
        print(f'{dt.isoformat()} | {message}') # Выводим Дату в ISO формате с заданный текстом на Консоль

    def __init__(self):
        """
        Инициализация Тогровой Системы (ТС)
        """
        self.order = None  # Заявка
        self.forecast = Forecast(self.datas[:30]) # сюда передать данные свечей
        self.trades = pd.DataFrame(columns=self.columns)
        self.orders = pd.DataFrame(columns=self.columns)

    def next(self):
        """
        Приход Нового Бара
        """
        self.log(f'Close = {self.datas[0].close[0]}')

        if self.order: # Если есть неисполненная Заявка # Выходим
            return

        predict = self.forecast.get_predict(self.datas[0])

        if not self.position:
            if predict: # Прогноз на Рост
                self.order = self.buy() # Заявка на Покупку по Рынку
            else: # Прогноз на Падение
                self.order = self.sell() # Заявка на Продажу по Рынку
        else:
            # Продолжаем Держать Позицию
            if (self.position.size > 0 and predict) or (self.position.size < 0 and not predict):
                return
            # Переворачиваемся
            self.order = self.close()
            if (self.position.size > 0 and not predict):
                self.log(f'Close LONG (SELL) Position: {self.position.size}')
                self.order = self.sell()
                self.log(f'Open SHORT (SELL) Position: {self.order.size}')
            elif (self.position.size < 0 and predict):
                self.log(f'Close SHORT (BYU) Position: {self.position.size}')
                self.order = self.buy()
                self.log(f'Open LONG (BYU) Position: {self.order.size}')

    def notify_order(self, order):
        """
        Уведомление об Изменении Статуса Заявки
        """
        if order.status in [order.Submitted, order.Accepted]: # Заявка Не Исполнена [ОтправленаБрокеру, ПринятаБрокером]
            return # то статус Заявки не меняем, выходим, дальше не продолжаем

        if order.status in [order.Completed]: # Заявка Исполнена
            message = f'Price={order.executed.price:.2f}, Size={order.executed.size:.6f}, Cost={order.executed.value:.2f}, Comm={order.executed.comm:.2f}'
            if order.isbuy():    # Заявка на Покупку
                self.log(f'BUY: {message}')
            elif order.issell(): # Заявка на Продажу
                self.log(f'SELL: {message}')
            self.BarExecuted = len(self) # Номер Бара, на котором была исполнена Заявка
        elif order.status in [order.Canceled, order.Margin, order.Rejected]: # Заявка [Отменена, НедостаточноСредств, ОтклоненаБрокером ]
            self.log('Canceled / Margin (Insufficient balance) / Rejected')
        self.add_order(order)
        self.order = None # Этой заявки больше нет

    def notify_trade(self, trade):
        """
        Уведомление об Изменении Статуса Позиции
        """
        if not trade.isclosed:  # Если позиция не закрыта
            return  # то статус позиции не изменился, выходим, дальше не продолжаем
        message = 'PPOFIT' if trade.pnlcomm >= 0 else 'LOSS'
        self.log(f'Trade closed with {message}, Gross={trade.pnl:.2f}, NET={trade.pnlcomm:.2f}')
        self.add_trade(trade)

    def add_trade(self, trade):
        side = 'LONG' if trade.long else 'SHORT'
        price_close = 0
        size = 0 # self.getposition(trade.data).size
        cost = 0
        # (trade.price, trade.pnl, trade.pnlcomm, trade.commission, trade.long)
        # ['side', 'price_open', 'price_close', 'size', 'cost', 'pnl', 'commis', 'pnlcomm']
        self.trades.loc[len(self.trades)] = (side, trade.price, price_close, size, cost, trade.pnl, trade.commission, trade.pnlcomm)


    def add_order(self, order):
        """
        order.info - Может ID в реальной торговле передается?
        ['side', 'open_price', 'close_price', 'size', 'cost', 'pnl', 'commis', 'pnlcomm']
        """
        side = 'BYU' if order.Buy else 'SELL'
        open_price = 0
        close_price = 0
        size = order.size
        cost = order.executed.value
        pnl = 0
        commis = 0
        pnlcomm = 0
        self.orders.loc[len(self.orders)] = (side, open_price, close_price, size, cost, pnl, commis, pnlcomm)



    def stop(self):
        sum_pnl = self.trades['pnl'].sum()
        sum_comm = self.trades['commis'].sum()
        sum_pnlcomm = self.trades['pnlcomm'].sum()
        mean_pnl = self.trades['pnl'].mean()
        mean_pnlcomm = self.trades['pnlcomm'].mean()

        print(self.trades)
        print(f'{sum_pnl = :.2f} | {sum_pnlcomm = :.2f} | {sum_comm = :.2f} || {mean_pnl = :.2f} | {mean_pnlcomm = :.2f}')
        print('-' * 100)
        # print(self.orders)




if __name__ == '__main__': # Точка Входа при запуске этого скрипта

    pd.options.display.width = None  # Отображение Таблицы на весь Экран
    pd.options.display.max_columns = 16  # Макс Кол-во Отображаемых Колонок
    pd.options.display.max_rows = 10  # Макс Кол-во Отображаемых Cтрок

    filename = 'F:\! PYTON\PyCharm\JupyterLab\data\ohlcvs\ETHUSDT_1d.csv'
    data = bt.feeds.PandasData(dataname=load_data(filename, start='2024-08-01', end=''))

    cerebro = bt.Cerebro()  # Инициализация "Движка" BackTrader (Cerebro = Мозг на испанском)
    cerebro.addstrategy(ForecastStrategy)  # Привязываем торговую систему с параметрами)
    cerebro.adddata(data) # Привязываем Исторические Данные (котировки и объемы)
    cerebro.addsizer(USDTSizer, usdt=1000, min_size=0.00001)  # Кол-во (Объем) Позиций
    cerebro.broker.setcommission(commission=0.001)  # Комиссия брокера 0.1% от суммы каждой исполненной заявки
    cerebro.broker.setcash(10000)  # Устанавливаем Стартовый Капитал
    print(f'Стартовый капитал: {cerebro.broker.getvalue():.0f}') # :.2f - точность 2 знака после десятичной точки
    cerebro.run() # Запуск ТС
    print(f'Конечный Капитал: {cerebro.broker.getvalue():.0f}')
    # Печать Графики Котировок+Объемы + Эквити + Сделки. // Требуется версия 3.2.2 matplotlib
    cerebro.plot(style='candle')  # style='candlestick' barup='green', subplot=False

