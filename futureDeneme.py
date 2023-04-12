import time
from binance.client import Client

client = Client('7230ERImQ0o2P7mexJIlI0980Qm7wBuapj1a7QBMFWZC7sVZ67aqiyoUrlITIpA9','AVKc2Dax37fIirVx9Yj3KeMyRB1uJzOw2L6Ksx2yARHIYV9VbYULTKUKN7SQ9Wod')

ticker = client.futures_symbol_ticker(symbol='BTCUSDT')
last_price = float(ticker['price'])
# print(last_price)
usdtEnter = 20
quantity = round(usdtEnter/last_price, 3) # 3 ondalık hane
print(quantity)
### Yukarıdaki işlemde kaç dolarla girmemiz gerektiğini öğrendik. 10x kaldıraçla girdiğimiz zaman usdt enteri 10'a bölersek bizim o işleme gireceğimiz miktarı buluruz.
### Kaç usdtlik girilecek == usdEnter / 10

#stop-loss fiyatını ve hedef fiyatını belirleyelim
"""stop_price = round(last_price * 0.95, 2) #piyasa fiyatının %5 altı
take_profit_price  = round(last_price * 1.05, 2) #piyasa fiyatının %5 üstü
print(stop_price)
print(take_profit_price)"""


order = client.futures_create_order(
    symbol='BTCUSDT',
    side='BUY',
    type='MARKET',
    quantity=quantity)

time.sleep(10)
print("Alım yapıldı")
#STOP_MARKET emri ile BTC satışı yapalım ve stop-loss emri ekleyelim
order = client.futures_create_order(
    symbol='BTCUSDT',
    side='SELL',
    type='STOP_MARKET',
    quantity=quantity,
    stopPrice=stop_price)

time.sleep(10)
print("stop loss yapıldı")



"""İşlemi kontrol etmek için açık pozisyonlarınızı listelemek için aşağıdaki kodu kullanabilirsiniz:"""
# positions = client.futures_position_information()
# print(positions)


"""Açık pozisyonlarınızı kapatmak için aşağıdaki kodu kullanabilirsiniz:"""

position_info = client.futures_position_information(symbol='BTCUSDT')
print(position_info)
time.sleep(60)
if position_info[0]['positionAmt'] != '0':
    #NOT short pozisyonunda "positionamt" < 0 olur. Long da ise > 0 olur. Ayrıyetten long pozisyonunu kapatmak için side Sell olmalıdır. Short pozisyonunu kapatmak için side Buy olmalıdır.
    order = client.futures_create_order(
        symbol='BTCUSDT',
        side='SELL',
        type='MARKET',
        quantity=quantity)