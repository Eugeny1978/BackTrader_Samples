import backtrader as bt
from random import randint


def get_line_names():
    names = []
    for i in range(1, 11):
        if i < 10:
            zero = '0'
        else:
            zero = ''
        names.append(f'name_{zero}{i}')
    names.append('forecast')
    names.append('up')
    names.append('dw')

    return tuple(names)

def set_plotlines(line_names):
    """
    Настройка Отображения Линий Индикатора на графике
    # alpha - интенсивность окраски, width - ширина бара #  linewidth=0.3,  edgecolor='black' - параметры matplotlib
    # _ методы с подчеркиванпием - параметры backtrader
    Настройка Убирает отображение вспомогательных линий
    Линия Прогноза отображается в виде Баров
    _method:
    'line' - стандартная линия, которая будет нарисована на графике.
    'bar' - линия будет нарисована в виде столбиков, отображая значения в виде вертикальных баров.
    'scatter' - точки будут нарисованы на графике в позиции значений.
    'step' - линия будет нарисована с учетом изменения значений, создавая эффект "крыльев" на графике.
    'area' - заполнит область под линией, создавая эффект "заполненной" линии.
    """
    plotlines = dict()
    for line in line_names:
        if line == 'forecast':
            plotlines[line] = dict(_method='bar', alpha=0.50, width=0.8,
                                   # _fill_gt=(0, 'green'),
                                   # _fill_lt=(1, 'red'),
                                   color='blue')  # , alpha=0.50, width=0.8
        elif line == 'up':
            plotlines[line] = dict(ls='', marker='o', color='green', markersize=8.0, fillstyle='full')
        elif line == 'dw':
            plotlines[line] = dict(ls='', marker='o', color='red', markersize=8.0, fillstyle='full')
        else:
            plotlines[line] = dict(_plotskip=True)
    return plotlines

def set_plotinfo():
    return dict(plot=True,
         subplot=True,  # отдельный подграфик
         plotname='FC',  # Имя индикатора
         plotabove=False,  # ниже основного графика
         plotlinelabels=False,
         plotlinevalues=True,  # отображение последнего значения в легенде
         plotvaluetags=False,  # ? отображение последнего значения справа
         plotymargin=0.1,  # отступ (доля от 1)
         plotyhlines=[],
         plotyticks=[0, 1],  #  Значения на шкале
         plothlines=[],
         plotforce=False,
         plotmaster=None,
         plotylimited=True,
         )



class ForecastIndicator(bt.Indicator):
    params = (('period', 30),)  # Параметры индикатора
    lines = get_line_names() #   # Определяем линии индикатора
    plotlines = set_plotlines(lines)
    plotinfo = set_plotinfo()


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

        if forecast:
            self.lines.up[0] = forecast
        else:
            self.lines.dw[0] = forecast





if __name__ == '__main__':

    import pandas as pd
    from bots.data_df import load_data

    pd.options.display.width = None  # Отображение Таблицы на весь Экран
    pd.options.display.max_columns = 16  # Макс Кол-во Отображаемых Колонок
    pd.options.display.max_rows = 10  # Макс Кол-во Отображаемых Cтрок

    filename = 'F:\! PYTON\PyCharm\JupyterLab\data\ohlcvs\ETHUSDT_1d.csv'
    data = bt.feeds.PandasData(dataname=load_data(filename, start='2024-07-01', end=''))

    cerebro = bt.Cerebro(stdstats=False)
    cerebro.adddata(data)

    # cerebro.addobserver(bt.observers.Trades)

    # fc = ForecastIndicator()
    # fc.plotinfo.plotname = 'ForeCast'
    # cerebro.addindicator(fc)

    cerebro.addindicator(ForecastIndicator)


    cerebro.run()
    cerebro.plot(style='candle')