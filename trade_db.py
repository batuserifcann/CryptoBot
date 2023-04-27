from telegramMesaj import *
from binance.client import Client
import numpy as np
import pandas as pd
import pandas_ta as ta
from datetime import datetime as dt
import csv
import time
import json
import requests
import sqlite3

conn = sqlite3.connect('sinyal.db', check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

client = Client('7230ERImQ0o2P7mexJIlI0980Qm7wBuapj1a7QBMFWZC7sVZ67aqiyoUrlITIpA9','AVKc2Dax37fIirVx9Yj3KeMyRB1uJzOw2L6Ksx2yARHIYV9VbYULTKUKN7SQ9Wod')
usdtEnter = 20
### Kaç usdtlik girilecek == usdEnter / 10

usdtGiris = usdtEnter / 10
# print(usdtGiris)


def zamanHesapla(zaman):
    zamanEpoch = zaman / 1000
    # zamanEpoch += 10800
    return dt.fromtimestamp(zamanEpoch)


semboller = ["BTCUSDT", "ETHUSDT", "BNBUSDT","DOGEUSDT","ANTUSDT","MANAUSDT","DOTUSDT","1INCHUSDT","ADAUSDT","XRPUSDT","AVAXUSDT","SOLUSDT"]


def verileriGetir(sembol, periyot, baslangic, bitis):
    mumlar = client.get_historical_klines(sembol, periyot, baslangic, bitis)
    # mumlar = client.get_historical_klines(sembol, periyot, )
    # print(mumlar)
    return mumlar


def csvOlustur(sembol, mumlar):
    csvDosya = open(sembol + ".csv", "w", newline="")
    yazici = csv.writer(csvDosya, delimiter=",")
    for mumVerileri in mumlar:
        yazici.writerow(mumVerileri)
    csvDosya.close()


def veriCekmeVeCsvOlusturma():
    for coin in semboller:
        csvOlustur(coin, verileriGetir(coin, Client.KLINE_INTERVAL_15MINUTE, "10 June 2000", "17 August 2030"))
        print(coin + " verileri getirildi")


def append_list_as_row(file_name, list_of_elem):
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = csv.writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)


def veriEkleme(coin, zaman):
    try:
        a = verileriGetir(coin, Client.KLINE_INTERVAL_15MINUTE, zaman, "17 August 2030")
        return a
    except Exception as E:
        print(E)
        time.sleep(5)
    # print(coin+" verileri getirildi")


def veriGüncelle():
    for coin in semboller:
        csvName = coin + ".csv"
        basliklar = ["open_time", "open", "high", "low", "close", "vol", "close_time", "qav", "nat", "tbbav", "tbqav",
                     "ignore"]
        with open(csvName, 'r') as f:
            last_line = f.readlines()[-1]
        sonElemanZaman = last_line[0:13]
        # print(sonElemanZaman)
        df = pd.read_csv(csvName)
        df.drop(df.tail(1).index, inplace=True)  # son satırı siliyoruz
        df.to_csv(csvName, index=False)  # indexleri siliyoruz
        zaman = str(zamanHesapla(int(sonElemanZaman)))
        # print(f"zaman : {zaman}")
        # time.sleep(5)
        yeniVeriler = veriEkleme(coin, zaman)
        yeniVerilerDF = pd.DataFrame(yeniVeriler, columns=basliklar)
        yeniVerilerDF.to_csv(csvName, index=False, mode='a', header=False)  # indexleri siliyoruz
        # for veri in yeniVeriler:


gonderilenSinyaller = {}
for coin in semboller:
    gonderilenSinyaller[coin] = "0"


def sinyalGonder(coin, zaman, mesaj):
    print(zaman)
    print(gonderilenSinyaller[coin])
    if zaman > int(gonderilenSinyaller[coin]):
        gonderilenSinyaller[coin] = zaman
        telegramMesajYolla(mesaj)


def alphaTrend_DF(df):  # CSV şeklinde gelen parite verileri
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    df["vol"] = df["vol"].astype(float)
    high = df["high"]
    low = df["low"]
    open = df["open"]
    close = df["close"]
    volume = df["vol"]
    open_time = df["open_time"]
    ap = 14
    tr = ta.true_range(high, low, close)
    atr = ta.sma(tr, ap)
    noVolumeData = False
    coeff = 1
    upt = []
    downT = []
    AlphaTrend = [0.0]
    src = close
    rsi = ta.rsi(src, 14)
    hlc3 = []
    k1 = []
    k2 = []
    mfi = ta.mfi(high, low, close, volume, 14)
    try:
        for i in range(len(close)):
            hlc3.append((high[i] + low[i] + close[i]) / 3)

        for i in range(len(low)):
            if pd.isna(atr[i]):
                upt.append(0)
            else:
                upt.append(low[i] - (atr[i] * coeff))
        for i in range(len(high)):
            if pd.isna(atr[i]):
                downT.append(0)
            else:
                downT.append(high[i] + (atr[i] * coeff))
        for i in range(1, len(close)):
            if noVolumeData is True and rsi[i] >= 50:
                if upt[i] < AlphaTrend[i - 1]:
                    AlphaTrend.append(AlphaTrend[i - 1])
                else:
                    AlphaTrend.append(upt[i])

            elif noVolumeData is False and mfi[i] >= 50:
                if upt[i] < AlphaTrend[i - 1]:
                    AlphaTrend.append(AlphaTrend[i - 1])
                else:
                    AlphaTrend.append(upt[i])
            else:
                if downT[i] > AlphaTrend[i - 1]:
                    AlphaTrend.append(AlphaTrend[i - 1])
                else:
                    AlphaTrend.append(downT[i])
    except Exception as e:
        print(e)
    for i in range(len(AlphaTrend)):
        if i < 2:
            k2.append(0)
            k1.append(AlphaTrend[i])
        else:
            k2.append(AlphaTrend[i - 2])
            k1.append(AlphaTrend[i])

    at = pd.DataFrame(data=k1, columns=['k1'])
    at['k2'] = k2
    return at


def trendHesapla_DF(df, coin):
    # try:
    try:
        
        key = f"https://api.binance.com/api/v3/ticker/price?symbol={coin}"

        data = requests.get(key)
        dataFiyat = data.json()
        coinAd = coin
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close"] = df["close"].astype(float)
        df["vol"] = df["vol"].astype(float)
        high = df["high"]
        low = df["low"]
        open = df["open"]
        close = df["close"]
        volume = df["vol"]
        acilisZamani = df["open_time"]

        # print(f"acilisZamani = {acilisZamani}")
        kapanis = df["close"]
        at = alphaTrend_DF(df)
        k1 = at["k1"]
        k2 = at["k2"]
        src = close
        rsi = ta.rsi(src, 14)
        sma = ta.sma(src, 14)
        mfi = ta.mfi(high, low, close, volume, 14)
        gecerliK1 = k1.tail(1)
        gecerliK2 = k2.tail(1)

        # print(rsi, mfi, gecerliK1, gecerliK2, sep=", ")

        sinyalSirasi = ["s"]  # al ile başlamasını istiyorum
        # print(at.shape[0])
        # sonAT = at.iloc[-1]
        # print(f"sonAT: {sonAT}")

        sonRSI = rsi.iloc[-1]
        # print(f"sonRSI: {sonRSI}")

        sonMFI = mfi.iloc[-1]
        # print(f"sonMFI: {sonMFI}")

        sonSMA = sma.iloc[-1]
        # print(f"sonSMA: {sonSMA}")

        diziBoyu = at.shape[0]
    except Exception as e:
        print(e)
        time.sleep(5)
    for i in range(diziBoyu - 1, diziBoyu):
        yazDiziSira = "Son Mum" if i == diziBoyu else f"{(diziBoyu - i)} mum once"
        if k1[i - 1] <= k2[i - 1] and k1[i] > k2[i] and k2[i] > 0 and sinyalSirasi[-1] != "a":
            # mesaj = f"{coinAd} AL SİNYALİ GELDİ\nFiyat : {dataFiyat['price']}\nRSI14 : {rsi[i]}\nMFI : {mfi[i]}\nZaman :  {zamanHesapla(acilisZamani[i])} "
        
            ticker = client.futures_symbol_ticker(symbol=coinAd)
            last_price = float(ticker['price'])
            if coinAd == "BTCUSDT":
                quantity = round(usdtEnter/last_price, 3) # 3 ondalık hane
                print(f"{coinAd} : {quantity}")
            elif coinAd == "ETHUSDT" or coinAd == "BNBUSDT":
                quantity = round(usdtEnter/last_price, 2) # 3 ondalık hane
                print(f"{coinAd} : {quantity}")
            else:
                quantity = round(usdtEnter/last_price) # 3 ondalık hane
                print(f"{coinAd} : {quantity}")
            try:
    
                order = client.futures_create_order(
                    symbol=coinAd,
                    side='BUY',
                    type='MARKET',
                    quantity=quantity)
                print(f"{coinAd} order created")
            except Exception as e:
                print(e)
                time.sleep(5)
            try:
                values = {
                    'parite': coinAd, 'alis_zamani': str(acilisZamani[i]), 'alis_fiyat': dataFiyat['price'],
                    'alis_rsi': rsi[i], 'alis_mfi': mfi[i], 'satis_zamani': None, 'satis_fiyat': None,
                    'satis_rsi': None, 'satis_mfi': None
                }
                cursor.execute(
                    """INSERT INTO sinyal_takip (parite,alis_zamani, alis_fiyat, alis_rsi, alis_mfi, satis_zamani, satis_fiyat, satis_rsi, satis_mfi)
                    VALUES (:parite, :alis_zamani, :alis_fiyat, :alis_rsi, :alis_mfi, :satis_zamani, :satis_fiyat, :satis_rsi, :satis_mfi);""",
                    values
                )
                # print(acilisZamani[i])
                print("EKLEME YAPILDI ----------------")
                telegramMesaj = f"{coinAd} alım yapıldı.\nFiyat : {dataFiyat['price']}"
                telegramMesajYolla(telegramMesaj)
                conn.commit()
            except Exception as e:
                print(e)

        # elif k1[i-1] >= k2[i-1] and k1[i] < k2[i] and sinyalSirasi[-1] != "s":
        #     mesaj = f"{coinAd} SAT SİNYALİ GELDİ\nFiyat : {data['price']}\nRSI14 : {rsi[i]}\nMFI : {mfi[i]}\nZaman :  {zamanHesapla(acilisZamani[i])} "
        #     #sinyalGonder(coinAd,acilisZamani[i],mesaj)
        #     # print(f"{yazDiziSira} sat için poz geldi {k2[i]} - {zamanHesapla(acilisZamani[i])}")
        #     sinyalSirasi.append("s")
        time.sleep(0.001)


# except Exception as E:
#     print(E)
#     print("Error")


def veriYaz():
    # her parite için dön:
    # parite son durumunu al (alış yapılmış mı ? fiyatBeklenti = pariteSatisBeklenti[parite]])
    # eğer fiyatBeklenti > 0 ise alış yapılmış satış için fırsat bekleniyor:
    # parite fiyatını getir
    # eğer parite fiyatı >= fiyatBeklenti:
    # satış işlemini yap. pariteSatisBeklenti[parite] = 0
    # değilse:
    # parite için alış fırsatı kovala
    # trend bilgisini bul (trendHesapla(parite))
    # eğer trend bilgisi al ise:
    # alış işlemini yap.
    # parite fiyatını getirildi
    # beklenti fiyatını hesapla (fiyat += fiyat * 0.01)
    # pariteSatisBeklenti[parite] = beklentiFiyati
    for coin in semboller:
        print(coin + " için çalışıyor")
        cursor.execute(
            f"SELECT * FROM sinyal_takip WHERE parite = '{coin}' and satis_zamani is NULL ORDER BY sira_id desc LIMIT 1")
        pariteAliBilgi = cursor.fetchone()
        if pariteAliBilgi != None:
            # print(pariteAliBilgi)
            try:
                pariteFiyatSorURL = f"https://api.binance.com/api/v3/ticker/price?symbol={coin}"
                pariteFiyatSor = requests.get(pariteFiyatSorURL)
                pariteFiyat = pariteFiyatSor.json()
                pariteAnlikFiyat = float(pariteFiyat['price'])
            except Exception as E:
                print(f"parite fiyatı alınamadı {E}")
                pariteAnlikFiyat = 0
            beklentiFiyat = float(pariteAliBilgi["alis_fiyat"]) * 1.01
            print(f"pariteAnlikFiyat: {pariteAnlikFiyat} - beklentiFiyat: {beklentiFiyat}")
            if pariteAnlikFiyat >= beklentiFiyat:
            
                ticker = client.futures_symbol_ticker(symbol=coin)
                last_price = float(ticker['price'])
                
                print(last_price)
                if coin == "BTCUSDT":
                    quantity = round(usdtEnter/last_price, 3) # 3 ondalık hane
                    print(f"{coin} : {quantity}")
                elif coin == "ETHUSDT" or coin == "BNBUSDT":
                    quantity = round(usdtEnter/last_price, 2) # 3 ondalık hane
                    print(f"{coin} : {quantity}")
                else:
                    quantity = round(usdtEnter/last_price) # 3 ondalık hane
                    print(f"{coin} : {quantity}")
                try:
                    order = client.futures_create_order(
                    symbol=coin,
                    side='SELL',
                    type='MARKET',
                    quantity=quantity)
                    print("order closed")
                except Exception as e:
                    print(e)
                print("satış işlemini gerçekleştir")
                values = {
                    'parite': coin, 'satis_zamani': str(time.time()), 'satis_fiyat': pariteAnlikFiyat,
                    'satis_rsi': 0, 'satis_mfi': 0
                }
                cursor.execute(
                    f"UPDATE sinyal_takip SET satis_zamani = ?, satis_fiyat = ?, satis_rsi = ?, satis_mfi = ?  WHERE parite = '{coin}' and satis_zamani is NULL",
                    (str(time.time()), pariteAnlikFiyat, 0, 0))
                print("Güncelleme yapıldı")
                telegramMesaj = f"{coin} satış yapıldı.\nFiyat : {pariteAnlikFiyat}"
                telegramMesajYolla(telegramMesaj)
                conn.commit()

            else:
                print("satış işlemi için fırsat bekleniyor")
        else:
            print("alış için fırsat bekleniyor")

            csvName = coin + ".csv"
            okunacakCsv = csvName
            basliklar = ["open_time", "open", "high", "low", "close", "vol", "close_time", "qav", "nat", "tbbav",
                         "tbqav",
                         "ignore"]
            df = pd.read_csv(okunacakCsv, names=basliklar, index_col=False,on_bad_lines='skip')
            # print(f"df:{df}")
            dataFrameMumSayisi = (len(df))
            sonMum = df.iloc[-1]
            sonMumCloseTime = int(sonMum["close_time"])
            # print("sonMum",sonMum["close_time"])
            yeniVeriler = veriEkleme(coin, sonMumCloseTime)

            # print(len(yeniVeriler))
            i = 0
            try:
                veriSayi = len(yeniVeriler)
            except Exception as e:
                print(e)
                time.sleep(5)
            while veriSayi > 1:
                eklenecekMum = yeniVeriler[i]
                # df.append(eklenecekMum, ignore_index = True)
                df.loc[dataFrameMumSayisi] = eklenecekMum
                # print("bekle")
                sonMum = df.iloc[-1:]
                # print(f"yeni eklenen mum {sonMum}")
                # print(len(df))
                yeniVerilerDF = pd.DataFrame(sonMum, columns=basliklar)
                yeniVerilerDF.to_csv(csvName, index=False, mode='a', header=False)  # indexleri siliyoruz
                # print(f"csv kaydedilen kayıtlı {eklenecekMum}")
                i += 1
                dataFrameMumSayisi += 1
                veriSayi -= 1

                # csv kayıT
            # son kaydıda ramdeki degere ekle
            try:
                eklenecekMum = yeniVeriler[i]
            except Exception as E:
                print(E)
                time.sleep(2)
            # print(f"eklenecekMum {eklenecekMum}")
            dataFrameMumSayisi = (len(df))
            df.loc[dataFrameMumSayisi] = eklenecekMum
            trendHesapla_DF(df, coin)

            # print(f"rame kayıtlı{df.iloc[-1:]}")


while True:
    veriYaz()
    time.sleep(1)