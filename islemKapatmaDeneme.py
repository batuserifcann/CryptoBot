import time
from binance.client import Client

client = Client('7230ERImQ0o2P7mexJIlI0980Qm7wBuapj1a7QBMFWZC7sVZ67aqiyoUrlITIpA9','AVKc2Dax37fIirVx9Yj3KeMyRB1uJzOw2L6Ksx2yARHIYV9VbYULTKUKN7SQ9Wod')
semboller = ["BTCUSDT", "ETHUSDT", "BNBUSDT","DOGEUSDT","ANTUSDT","MANAUSDT","DOTUSDT","1INCHUSDT","ADAUSDT","XRPUSDT","AVAXUSDT","SOLUSDT"]


usdtEnter = 20
### Kaç usdtlik girilecek == usdEnter / 10

usdtGiris = usdtEnter / 10
# print(usdtGiris)

for symbol in semboller:
    
    ticker = client.futures_symbol_ticker(symbol=symbol)
    last_price = float(ticker['price'])
    
    print(last_price)
    if symbol == "BTCUSDT":
        quantity = round(usdtEnter/last_price, 3) # 3 ondalık hane
        print(f"{symbol} : {quantity}")
    elif symbol == "ETHUSDT" or symbol == "BNBUSDT":
        quantity = round(usdtEnter/last_price, 2) # 3 ondalık hane
        print(f"{symbol} : {quantity}")
    else:
        quantity = round(usdtEnter/last_price) # 3 ondalık hane
        print(f"{symbol} : {quantity}")
    #### İŞLEM AÇMA
    try:
        
        order = client.futures_create_order(
            symbol=symbol,
            side='BUY',
            type='MARKET',
            quantity=quantity)
        print("order created")
    except Exception as e:
        print(e)
        time.sleep(5)
    #### İŞLEM KAPATMA
    try:
        order = client.futures_create_order(
        symbol=symbol,
        side='SELL',
        type='MARKET',
        quantity=quantity)
        print("order closed")
    except Exception as e:
        print(e)
# print(last_price)

### Yukarıdaki işlemde kaç dolarla girmemiz gerektiğini öğrendik. 10x kaldıraçla girdiğimiz zaman usdt enteri 10'a bölersek bizim o işleme gireceğimiz miktarı buluruz.



# order = client.futures_create_order(
#         symbol='BNBUSDT',
#         side='SELL',
#         type='MARKET',
#         quantity=quantity)