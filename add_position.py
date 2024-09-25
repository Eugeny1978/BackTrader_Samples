import datetime
import backtrader as bt # Библиотека BackTrader (pip install backtrader)

class PriceMACross(bt.Strategy):
    ''' Пересечение цены и SMA '''
    params = (('SMAPeriod', 30), ('AddSize', 0.5), ('NumAdds', 5))

    def log(self, txt, dt=None):
        ''' Вывод строки с Датой на Консоль '''
        dt = dt or self.datas[0].datetime.date() # Заданная Дата или Дата Текущего Бара
        print(f'{dt.isoformat()}, {txt}') # Выводим Дату в ISO формате с заданный текстом на Консоль

    def __init__(self):
        ''' Инициализация Тогровой Системы (ТС) '''
        self.DataClose = self.datas[0].close
        self.Order = None # Заявка
        self.SMA = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.SMAPeriod)  # SMA

    def notify_order(self, order):
        ''' Изменение Статуса Заявки '''
        if order.status in [order.Submitted, order.Accepted]: # Заявка Не Исполнена [ОтправленаБрокеру, ПринятаБрокером]
            return # то статус Заявки не меняем, выходим, дальше не продолжаем

        if order.status in [order.Completed]: # Заявка Исполнена
            if order.isbuy():    # Заявка на Покупку
                self.log(f'Bought @{order.executed.price:.2f}, Cost={order.executed.value:.2f}, Comm={order.executed.comm:.2f}')
            elif order.issell(): # Заявка на Продажу
                self.log(f'Sold @{order.executed.price:.2f}, Cost={order.executed.value:.2f}, Comm={order.executed.comm:.2f}')
            self.BarExecuted = len(self) # Номер Бара, на котором была исполнена Заявка
        elif order.status in [order.Canceled, order.Margin, order.Rejected]: # Заявка [Отменена, НедостаточноСредств, ОтклоненаБрокером ]
            self.log('Canceled/Margin/Rejected')
        self.Order = None # Этой заявки больше нет

    def notify_trade(self, trade):
        ''' Изменение статуса позиции '''
        if not trade.isclosed:  # Если позиция не закрыта
            return  # то статус позиции не изменился, выходим, дальше не продолжаем
        if trade.pnlcomm >= 0:
            self.log(f'Trade closed with PPOFIT, Gross={trade.pnl:.2f}, NET={trade.pnlcomm:.2f}')
        else:
            self.log(f'Trade closed with LOSS, Gross={trade.pnl:.2f}, NET={trade.pnlcomm:.2f}')

    def next(self):
        ''' Приход Нового Бара '''
        self.log(f'Close={self.DataClose[0]:.0f}')

        if self.Order: # Если есть неисполненная Заявка
            return     # Выходим

        if not self.position: # Позиции НЕТ
           isSignalBuy = (self.DataClose[0] > self.SMA[0]) # Цена Закрытия Больше SMA
           if isSignalBuy:  # Есть Сигнал на Покупку
               self.log('Buy Market')
               self.Order = self.buy() # Заявка на Покупку по Рынку
        else: # Позиция Есть (Открыта)
            isSignalSell = (self.DataClose[0] < self.SMA[0])  # Цена Закрытия Меньше SMA
            if isSignalSell:
                self.log('Sell Market')
                self.Order = self.sell() # Заявка на Продажу по Рынку

if __name__ == '__main__': # Точка Входа при запуске этого скрипта

    path_to_file = 'F:/! PYTON/Котировки/BTCUSDT_1Day.csv'
    data = bt.feeds.GenericCSVData(
        dataname=path_to_file,
        separator=';',  # Колонки разделены ";"
        dtformat='%Y-%m-%d',  # Одна колонка (Дата и Время):  %H:%M
        openinterest=-1,  # Открытого интереса в файле нет
        fromdate=datetime.datetime(2021, 1, 1),  # начальная дата (входит)
        todate=datetime.datetime(2021, 5, 29))  # конечная дата (не входит)

    cerebro = bt.Cerebro()  # Инициализация "Движка" BackTrader (Cerebro = Мозг на испанском)
    cerebro.addstrategy(PriceMACross, SMAPeriod=30)  # Привязываем торговую систему с параметрами)
    cerebro.adddata(data) # Привязываем Исторические Данные (котировки и объемы)
    cerebro.addsizer(bt.sizers.FixedSize, stake=0.1)  # Кол-во (Объем) акций для покупки/продажи
    cerebro.broker.setcommission(commission=0.001)  # Комиссия брокера 0.1% от суммы каждой исполненной заявки
    cerebro.broker.setcash(10000)  # Устанавливаем Стартовый Капитал
    print(f'Стартовый капитал: {cerebro.broker.getvalue():.0f}') # :.2f - точность 2 знака после десятичной точки
    cerebro.run() # Запуск ТС
    print(f'Конечный Капитал: {cerebro.broker.getvalue():.0f}')
    cerebro.plot(style='candlestick') # Печать Графики Котировок+Объемы + Эквити + Сделки. // Требуется версия 3.2.2 matplotlib #