import backtrader as bt

class MyCustomIndicator(bt.Indicator):
    lines = ('myind',)  # Определяем линии индикатора
    params = (('period', 14),)  # Параметры индикатора

    def __init__(self):
        # Вычисляем значение индикатора
        self.addminperiod(self.params.period)  # Минимальный период для расчета индикатора

    def next(self):
        # Далее идет логика расчета значения индикатора
        if len(self.data) >= self.params.period:
            self.lines.myind[0] = sum(self.data.close.get(-i) for i in range(self.params.period)) / self.params.period

class MyStrategy(bt.Strategy):
    def __init__(self):
        # Инициализация индикатора
        self.my_custom_indicator = MyCustomIndicator(period=14)

    def next(self):
        # Использование значения индикатора в торговой логике
        if self.my_custom_indicator.myind[0] > self.data.close[0]:
            self.buy()
        elif self.my_custom_indicator.myind[0] < self.data.close[0]:
            self.sell()

## ----------------------------


from random import randint

class Forecast(object):
    """
    Создай его как свой Индикатор! - См КОД ВЫШЕ
    """

    def __init__(self, datas):
        self.datas = datas

    def get_predict(self, datas):
        return randint(0, 1)


if __name__ == '__main__':

    f = Forecast([4, 5 ,6])
    for i in range(20):
        print(f.get_predict([4, 6, 8]))
