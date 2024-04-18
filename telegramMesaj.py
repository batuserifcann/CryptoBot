import requests
from telegram.ext import Updater
telegramBotChatID = "873908419"
kanalId= ""
telegramBotToken  = ""

updater = Updater(telegramBotToken, use_context=True)

def telegramMesajYolla(mesaj="Tanimsiz"):
  global updater
  updater.dispatcher.bot.send_message(telegramBotChatID , mesaj)
