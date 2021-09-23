import telebot
from telebot import types
import random
import time
import sys
import requests

class alerts:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

TOKEN = '2003590639:AAHZjxZrXc8ZoAYW2_RvOIlwfmJ3xE4bkt8' 
print("Идет запуск бота... ")
print(alerts.OKCYAN + "Пожалуйста, подождите!" + alerts.ENDC)
url = "https://google.com"

timeout = 3

try:

	request = requests.get(url, timeout=timeout)

	print(alerts.OKGREEN + "Идет запуск хоста" + alerts.ENDC)

except (requests.ConnectionError, requests.Timeout) as exception:

	print(alerts.FAIL+ "Ошибка при подключении к интернету!" + alerts.ENDC)
	print(alerts.FAIL+ "ПОЛНАЯ ОШИБКА:" + alerts.ENDC)
	

bot = telebot.TeleBot('2003590639:AAHZjxZrXc8ZoAYW2_RvOIlwfmJ3xE4bkt8')

usersQueue = []
usersPlaying = []
allQuestioners = []
questions = {}
userIds = {}

startKeyboardMarkupInline = types.InlineKeyboardMarkup()
btnStart = types.InlineKeyboardButton("Начать игру", callback_data="game start")
startKeyboardMarkupInline.row(btnStart)

emptyInline = types.InlineKeyboardMarkup()


# startKeyboardMarkup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
# btn1 = types.KeyboardButton('Начать игру')
# startKeyboardMarkup.row(btn1)


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    global startKeyboardMarkupInline
    bot.send_message(message.from_user.id, "Данный бот является игрой. Викториной со случайными оппонентами. "
                                           "После того, как будет найден оппонент, случайным образом определится, "
                                           "кто будет ведущим (задавать вопрос), "
                                           "а кто будет отвечающим (отвечать на вопрос).")
    bot.send_message(message.from_user.id, "Желаете сыграть?",
                     reply_markup=startKeyboardMarkupInline)


@bot.callback_query_handler(func=lambda call: call.data == "game start")
def game_start_callback(call):
    global emptyInline
    global usersQueue
    global userIds

    if call.from_user.id in usersQueue:
        return 7
    userIds[call.from_user.id] = call.from_user.username
    usersQueue.append(call.from_user.id)
    print("usersQueue", usersQueue)
    bot.edit_message_reply_markup(chat_id=call.from_user.id,
                                  message_id=call.message.message_id,
                                  reply_markup=emptyInline)
    bot.send_message(call.from_user.id, "Идет поиск оппонентов, начало викторины...")

    if len(usersQueue) > 1:
        player1 = usersQueue.pop(0)
        player2 = usersQueue.pop(0)
        start_game(player1, player2)


def start_game(player1, player2):
    global allQuestioners
    global usersPlaying
    global userIds

    players = [player1, player2]
    random.shuffle(players)
    questioner = players[0]
    answerer = players[1]
    usersPlaying.append([questioner, answerer])
    print("usersPlaying:", usersPlaying)
    allQuestioners.append(questioner)

    bot.send_message(questioner, "Оппонент найден\nВаш оппонент: " + userIds[answerer])
    bot.send_message(answerer, "Оппонента найден\nВаш оппонент: " + userIds[questioner])

    bot.send_message(questioner, "Напишите вопрос")
    bot.send_message(answerer, "Ждите пока оппонент задаст вопрос")


@bot.message_handler(content_types=['text'])
def question_handler(message):
    questioner = message.from_user.id
    answerer = None
    if questioner in allQuestioners:
        if questioner not in questions:
            questions[questioner] = [message.text]
            bot.send_message(questioner, "Напишите правильный вариант ответа")
        else:
            questions[questioner].append(message.text)
            if len(questions[questioner]) <= 2:
                bot.send_message(questioner, "Напишите неправильный вариант ответа")
            elif len(questions[questioner]) <= 3:
                bot.send_message(questioner, "Напишите еще один неправильный вариант ответа")
            else:
                for pair in usersPlaying:
                    if questioner in pair:
                        answerer = pair[1]
                answersInline = types.InlineKeyboardMarkup()
                answers = [questions[questioner][1], questions[questioner][2], questions[questioner][3]]
                random.shuffle(answers)
                btn1 = types.InlineKeyboardButton(answers[0], callback_data=answers[0])
                btn2 = types.InlineKeyboardButton(answers[1], callback_data=answers[1])
                btn3 = types.InlineKeyboardButton(answers[2], callback_data=answers[2])
                answersInline.row(btn1)
                answersInline.row(btn2)
                answersInline.row(btn3)

                bot.send_message(answerer, questions[questioner][0], reply_markup=answersInline)
                bot.send_message(questioner, "Вопрос отправлен оппоненту")
    else:
        bot.send_message(message.from_user.id, "Желаете сыграть?", reply_markup=startKeyboardMarkupInline)


@bot.callback_query_handler(func=lambda call: call.data != "game start")
def answer_callback(call):
    global questions
    global usersPlaying

    answerer = call.from_user.id
    questioner = None
    for players in usersPlaying:
        if answerer in players:
            questioner = players[0]

    editedInline = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(u'\u2714' + " " + questions[questioner][1], callback_data="133")
    btn2 = types.InlineKeyboardButton(u'\u274C' + " " + questions[questioner][2], callback_data="133")
    btn3 = types.InlineKeyboardButton(u'\u274C' + " " + questions[questioner][3], callback_data="133")
    editedInline.row(btn1)
    editedInline.row(btn2)
    editedInline.row(btn3)
    bot.edit_message_reply_markup(chat_id=answerer,
                                  message_id=call.message.message_id,
                                  reply_markup=editedInline)

    playAgainMarkup = types.InlineKeyboardMarkup()
    playAgainBtn = types.InlineKeyboardButton("Сыграть снова", callback_data="game start")
    playAgainMarkup.row(playAgainBtn)
    if call.data == questions[questioner][1]:
        bot.send_message(answerer, 'Вы ответили:\n' + call.data)
        bot.send_message(answerer, 'Ответ верный!', reply_markup=playAgainMarkup)
        bot.send_message(questioner, "Отвечающий ответил верно!", reply_markup=playAgainMarkup)
    else:
        bot.send_message(answerer, 'Вы ответили:\n' + call.data)
        bot.send_message(answerer, 'Ответ неверный!\nВерный ответ:\n' + questions[questioner][1],
                         reply_markup=playAgainMarkup)
        bot.send_message(questioner, "Отвечающий ответил неверно!\nВыбранный им ответ:\n" + call.data,
                         reply_markup=playAgainMarkup)

    usersPlaying.remove([questioner, answerer])
    allQuestioners.remove(questioner)
    questions.pop(questioner)


if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
            time.sleep(3)
