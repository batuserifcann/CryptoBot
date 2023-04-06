import time
from binance.client import Client

client = Client('7230ERImQ0o2P7mexJIlI0980Qm7wBuapj1a7QBMFWZC7sVZ67aqiyoUrlITIpA9','AVKc2Dax37fIirVx9Yj3KeMyRB1uJzOw2L6Ksx2yARHIYV9VbYULTKUKN7SQ9Wod')

ticker = client.futures_symbol_ticker(symbol='BTCUSDT')
last_price = float(ticker['price'])
print(last_price)
usdtEnter = 20
quantity = round(usdtEnter/last_price, 3) # 3 ondalık hane
print(quantity)
### Yukarıdaki işlemde kaç dolarla girmemiz gerektiğini öğrendik. 10x kaldıraçla girdiğimiz zaman usdt enteri 10'a bölersek bizim o işleme gireceğimiz miktarı buluruz.
### Kaç usdtlik girilecek == (quantity * last_price) / 10

order = client.futures_create_order(
    symbol='BTCUSDT',
    side='BUY',
    type='MARKET',
    quantity=quantity)


"""İşlemi kontrol etmek için açık pozisyonlarınızı listelemek için aşağıdaki kodu kullanabilirsiniz:"""
# positions = client.futures_position_information()
# print(positions)


"""Açık pozisyonlarınızı kapatmak için aşağıdaki kodu kullanabilirsiniz:"""
position_info = client.futures_position_information(symbol='BTCUSDT')
print(position_info)
if position_info[0]['positionAmt'] != '0':
    # side = 'SELL' if position_info[0]['positionSide'] == 'LONG' else 'BUY'
    # quantity = abs(float(position_info[0]['positionAmt']))
    order = client.futures_create_order(
        symbol='BTCUSDT',
        side='SELL',
        type='MARKET',
        quantity=quantity)