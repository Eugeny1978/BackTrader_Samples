import ccxt
from datetime import datetime
from time import sleep

exchange1 = ccxt.mexc() # ccxt.bybit()
exchange2 = ccxt.bitteam()
pair= 'DEL/USDT' # 'ETH/USDT'
limit=1

def get_datetime_now() -> str:
    return datetime.now().strftime('%Y-%m-%d | %H:%M:%S')

while True:
    dt = get_datetime_now()
    DATA=[exchange1.fetch_order_book(pair,limit), exchange2.fetch_order_book(pair, limit)]
    bids=[]
    asks=[]
    for data in DATA:
        bids.append(data['bids'][0])
        asks.append(data['asks'][0])
    delta_1 = round(((asks[0][0] - bids[1][0]))/asks[0][0]*100, 4)
    delta_2 = round(((bids[0][0] - asks[1][0]))/bids[0][0]*100, 4)

    print(f"{dt} | {pair} | Разница Цен между Биржами  ASK {exchange1} | BID {exchange2} = {delta_1}%",)
    print(f"{dt} | {pair} | Разница Цен между Биржами  BID {exchange1} | ASK {exchange2} = {delta_2}%",)
    print('-' * 150)
    sleep(10)