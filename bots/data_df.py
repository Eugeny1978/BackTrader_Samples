import pandas as pd
from datetime import datetime

# Загрузите данные из CSV
def load_data(filename: str, start: str='', end: str='') -> pd.DataFrame:
    """
    :param filename: Путь к файлу
    :param start: Начало Интервала
    :param end: Конец Интервала
    """
    df = pd.read_csv(filename, sep=';') # Чтение CSV с помощью pandas
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms') # из timestamp в datetime
    df = df.drop(columns=['timestamp']) # Удалию старый столбец timestamp

    # Интервал
    if not start:
        start_index = 0
    else:
        start = datetime.strptime(start, '%Y-%m-%d')
        start_index = min(df.loc[df['datetime'] >= start].index)
    if not end:
        end_index = len(df)
    else:
        end = datetime.strptime(end, '%Y-%m-%d')
        end_index = max(df.loc[df['datetime'] <= end].index)+1
    df = df.iloc[start_index : end_index]

    df.set_index('datetime', inplace=True) # datetime в качестве индекса

    return df

if __name__ == '__main__':

    file = 'F:\! PYTON\PyCharm\JupyterLab\data\ohlcvs\ETHUSDT_1d.csv'
    # df = load_data(file)
    df = load_data(file, start='2020-01-05', end='2023-12-07')
    print(df)