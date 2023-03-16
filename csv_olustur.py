from telegramMesaj import *
from binance.client import Client
import numpy as np
import pandas as pd
import pandas_ta as ta
from datetime import datetime as dt
import csv
import time

client = Client("","")


def zamanHesapla(zaman):
    zamanEpoch = zaman / 1000
    zamanEpoch -= 10800
    return dt.fromtimestamp(zamanEpoch)


semboller = ["BTCUSDT", "ETHUSDT", "BNBUSDT",]

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


semboller = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "SOLUSDT", "DOGEUSDT", "DAIUSDT", "SHIBUSDT",
             "DOTUSDT", "AVAXUSDT", "MANAUSDT", "1INCHUSDT", "ANTUSDT"]


def veriCekmeVeCsvOlusturma():
    for coin in semboller:
        csvOlustur(coin, verileriGetir(coin, Client.KLINE_INTERVAL_15MINUTE, "10 June 2000", "17 August 2030"))
        df = pd.read_csv(f'{coin}.csv')
        df.drop(df.tail(1).index, inplace=True)
        print(coin + " verileri getirildi")


def append_list_as_row(file_name, list_of_elem):
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = csv.writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)


def veriEkleme(zaman):
    # for coin in semboller:
    a = verileriGetir("1INCHUSDT", Client.KLINE_INTERVAL_4HOUR, zaman, "17 August 2030")
    return a
    # print(coin+" verileri getirildi")


def veriGüncelle():
    csvName = "1INCHUSDT.csv"
    basliklar = ["open_time", "open", "high", "low", "close", "vol", "close_time", "qav", "nat", "tbbav", "tbqav",
                 "ignore"]
    with open(csvName, 'r') as f:
        last_line = f.readlines()[-1]
    sonElemanZaman = last_line[0:13]
    #print(sonElemanZaman)
    df = pd.read_csv('1INCHUSDT.csv')
    df.drop(df.tail(1).index, inplace=True)  # son satırı siliyoruz
    df.to_csv('1INCHUSDT.csv', index=False)  # indexleri siliyoruz
    zaman = str(zamanHesapla(int(sonElemanZaman)))
    #print(f"zaman : {zaman}")
    #time.sleep(5)
    yeniVeriler = veriEkleme(zaman)
    yeniVerilerDF = pd.DataFrame(yeniVeriler, columns=basliklar)
    yeniVerilerDF.to_csv('1INCHUSDT.csv', index=False, mode='a', header=False)  # indexleri siliyoruz
    # for veri in yeniVeriler:
    # print(veri)


veriCekmeVeCsvOlusturma()
