import requests
from telegram.ext import Updater
telegramBotChatID = "873908419"
kanalId= "-1001741371381"
telegramBotToken  = "5705765467:AAFDIKXIBkDK0qXz7q2cNxSLTKqKYLyksN8"

updater = Updater(telegramBotToken, use_context=True)

def telegramMesajYolla(mesaj="Tanimsiz"):
  global updater
  updater.dispatcher.bot.send_message(telegramBotChatID , mesaj)
