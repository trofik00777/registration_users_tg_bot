import pymysql
import telebot
from telebot import types
from telebot.types import Message

from string import punctuation

TOKEN = ""

bot = telebot.TeleBot(TOKEN)

users = dict()


@bot.message_handler(commands=["start", "help"])
def start(message: Message):
    users[f"{message.from_user.id}"] = {"name": "", "surname": ""}
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add(types.KeyboardButton("a", request_location=True))
    bot.send_message(message.chat.id, "Привет, это тестовый бот регистрации пользователей")
    m = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    m.add(types.KeyboardButton("Зарегестрироваться"), types.KeyboardButton("Вывести бд"), types.KeyboardButton("Поиск"))
    msg = bot.send_message(message.chat.id, "Выбери режим",
                           reply_markup=m)
    bot.register_next_step_handler(message=msg,
                                   callback=choose)


def choose(message: Message):
    text = message.text
    if text == "Зарегестрироваться":
        msg = bot.send_message(message.chat.id, text="Введите имя:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(message=msg,
                                       callback=registr_name)
    elif text == "Вывести бд":
        try:
            con = pymysql.connect("localhost", "root", "", "first_tg_bot_test")
            with con:
                cur = con.cursor()
                cur.execute("SELECT * FROM `test_table`")
                data = cur.fetchall()
            for i in data:
                try:
                    bot.send_message(message.chat.id, " ".join(i))
                except Exception as e:
                    print(e)
        except:
            bot.send_message(message.chat.id, "Проблемы с соединением с сервером")
    else:
        m = types.ForceReply(selective=False)
        msg = bot.send_message(message.chat.id, "Введите имя или фамилию")
        bot.register_next_step_handler(message=msg,
                                       callback=search)


def search(message: Message):
    text = message.text.capitalize()
    try:
        con = pymysql.connect("localhost", "root", "", "first_tg_bot_test")
        with con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM `test_table` WHERE name = \"{text}\" OR surname = \"{text}\"")
            data = cur.fetchall()
            for i in data:
                try:
                    bot.send_message(message.chat.id, " ".join(i))
                except Exception as e:
                    print(e)

    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "Проблемы с соединением с сервером")


def registr_name(message: Message):
    global users
    users[f"{message.from_user.id}"]["name"] = message.text.strip()
    m = types.ForceReply(selective=False)
    msg = bot.send_message(message.chat.id, "Введи фамилию:", reply_markup=m)
    bot.register_next_step_handler(message=msg,
                                   callback=registr_surname)


def registr_surname(message: Message):
    global users
    users[f"{message.from_user.id}"]["surname"] = message.text.strip()
    m = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    m.add(types.KeyboardButton("Зарегестрироваться"), types.KeyboardButton("Отмена"))
    msg = bot.send_message(message.chat.id, "Выберите ответ:", reply_markup=m)
    bot.register_next_step_handler(message=msg,
                                   callback=reg)


def reg(message: Message):
    text = message.text
    global users
    print(users)
    print([i for i in users[f"{message.from_user.id}"]["name"] + users[f"{message.from_user.id}"]["surname"] if i in punctuation])
    if text == "Отмена":
        users[f"{message.from_user.id}"]["name"] = ""
        users[f"{message.from_user.id}"]["surname"] = ""
    else:
        if (users[f"{message.from_user.id}"]["name"].strip() and
            users[f"{message.from_user.id}"]["surname"].strip() and
                [i for i in users[f"{message.from_user.id}"]["name"] + users[f"{message.from_user.id}"]["surname"] if i  in punctuation] == []):
            try:
                con = pymysql.connect("localhost", "root", "", "first_tg_bot_test")
                with con:
                    cur = con.cursor()
                    cur.execute(f"INSERT INTO `test_table` VALUES ('{users[f'{message.from_user.id}']['name'].capitalize()}', '{users[f'{message.from_user.id}']['surname'].capitalize()}')")
                    bot.send_message(message.chat.id, "Вы успешно зарегестрированы")
            except:
                bot.send_message(message.chat.id, "Проблемы с соединением с сервером")
        else:
            msg = bot.send_message(message.chat.id, "Введите данные заново")
            bot.register_next_step_handler(message=msg,
                                           callback=start)


bot.polling()
