import telebot
import types
import os
from nickname_generator import generate
# print(generate())

bot = os.environ(telebot.TeleBot(TOKEN))
print('bot started')

@bot.message_handler(commands=['start'])
def send_welcome(message):
	bot.reply_to(message, "Привет,  c помощью этого бота ты можешь сгенерировать подходящий никнейм! Все команды: /help")
@bot.message_handler(commands=['gen'])
def send_welcome(message):
	bot.reply_to(message, generate())
	
@bot.message_handler(commands=['help'])
def send_welcome(message):
	bot.reply_to(message, "Все команды: \n\n |-Создать никнейм:  /gen \n |-Это сообщение: /help \n |-Информация о  сессии /session")

@bot.message_handler(commands=['session'])
def send_welcome(message):
	bot.reply_to(message, message)

bot.infinity_polling()
