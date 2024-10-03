import backtrader as bt
import pandas as pd
from random import randint

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

class ForecastIndicator(bt.Indicator):
    lines = ('forecast', )  # Определяем линии индикатора
    params = (('period', 30), )  # Параметры индикатора
    # Отображение Индикатора на графике
    # alpha - интенсивность окраски, width - ширина бара
    plotlines = dict(forecast=dict(_method='bar', alpha=0.50, width=0.8, color='green')) #  linewidth=0.3,  edgecolor='black'
    plotinfo = dict(plot=True,
                    subplot=True, # отдельный подшрафик
                    plotname='FC', # Имя индикатора
                    plotabove=False, # ниже основного графика
                    plotlinelabels=False,
                    plotlinevalues=True,
                    plotvaluetags=True,
                    plotymargin=0.1, # отступ (доля от 1)
                    plotyhlines=[],
                    plotyticks=[0, 1], # Значения на шкале
                    plothlines=[],
                    plotforce=False,
                    plotmaster=None,
                    plotylimited=True,
                    )

    def __init__(self):
        # Вычисляем значение индикатора
        self.addminperiod(self.params.period)  # Минимальный период для расчета индикатора

    def next(self):
        """
        Расчет значения индикатора при поступлении новой Свечи
        """
        if len(self.data) < self.params.period: return # Проверка на мин кол-во баров

        forecast = randint(0,1)

        self.lines.forecast[0] = forecast


class ForecastStrategy(bt.Strategy):
    params = (
        ('history', True),  # Или False, если не хотите сохранять историю
        ('historyon', True)  # Или False, если не хотите сохранять историю операций
    )

    trade_columns = ['dt', 'side', 'price', 'pnl', 'commis', 'pnlcomm']
    def __init__(self):
        self.indicator = ForecastIndicator() # Инициализация индикатора
        self.order = None
        self.trades = pd.DataFrame(columns=self.trade_columns)

    def next(self):
        """
        Использование значения индикатора в торговой логике
        """
        if self.position:
            self.order = self.close(historyon=True)
        if self.indicator.forecast[0]:
            self.order = self.buy(historyon=True) # history=True,
        else:
            self.order = self.sell(historyon=True)

    def notify_order(self, order):
        # if order.status in [order.Completed]:
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:  # Если позиция не закрыта
            return  # то статус позиции не изменился, выходим, дальше не продолжаем
        if trade.isclosed:
            size = trade.size
        self.add_trade(trade)

    def add_trade(self, trade):
        dt = self.datas[0].datetime.date()
        side = 'LONG' if trade.long else 'SHORT'
        price = trade.price
        pnl = trade.pnl
        commis = trade.commission
        pnlcomm = trade.pnlcomm
        # (trade.price, trade.pnl, trade.pnlcomm, trade.commission, trade.long)
        # ['dt', 'side', 'price', 'pnl', 'commis', 'pnlcomm']
        self.trades.loc[len(self.trades)] = (dt, side, price, pnl, commis, pnlcomm)


    def stop(self):
        print(self.trades)


if __name__ == '__main__':

    import pandas as pd
    from data_df import load_data


    pd.options.display.width = None  # Отображение Таблицы на весь Экран
    pd.options.display.max_columns = 16  # Макс Кол-во Отображаемых Колонок
    pd.options.display.max_rows = 10  # Макс Кол-во Отображаемых Cтрок

    filename = 'F:\! PYTON\PyCharm\JupyterLab\data\ohlcvs\ETHUSDT_1d.csv'
    data = bt.feeds.PandasData(dataname=load_data(filename, start='2024-05-01', end=''))

    cerebro = bt.Cerebro()
    cerebro.addstrategy(ForecastStrategy)
    cerebro.adddata(data)
    cerebro.addsizer(USDTSizer, usdt=1000, min_size=0.00001)  # Кол-во (Объем) Позиций
    cerebro.broker.setcommission(commission=0.001)  # Комиссия брокера 0.1% от суммы каждой исполненной заявки
    cerebro.broker.setcash(10000)  # Устанавливаем Стартовый Капитал

    cerebro.run() # Запуск ТС
    cerebro.plot(style='candle')