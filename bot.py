import telebot
import helpers
import time
import sqlite3

API_TOKEN = '1725219040:AAGFuicW0cXzJXVLLJK1qVJxO_1uBElU2Vk'

bot = telebot.TeleBot(API_TOKEN)


def getUser(chat_id):
    with sqlite3.connect("db.sqlite") as con:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM users WHERE chat_id = ?", (chat_id,))
        result = cursor.fetchone()
        return result


def getAllUsers():
    with sqlite3.connect("db.sqlite") as con:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM users")
        result = cursor.fetchall()
        return result


def createUser(chat_id, phone, name):
    with sqlite3.connect("db.sqlite") as con:
        cursor = con.cursor()
        cursor.execute("INSERT INTO users (chat_id, phone, draft) VALUES (? , ?, ?)", (chat_id, phone, name))
        con.commit()


@bot.message_handler(commands=['start'])
def command_start(message):
    if getUser(message.chat.id) is None:
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add(telebot.types.KeyboardButton('Отправить свой номер', request_contact=True))
        bot.send_message(message.chat.id, 'Пожалуйста отправьте свой номер', reply_markup=markup)


@bot.message_handler(content_types=['contact'])
def contact(message):
    if message.contact is not None and getUser(message.chat.id) is None:
        phone = message.contact.phone_number
        telebot.types.ReplyKeyboardRemove()
        msg = bot.send_message(message.chat.id, 'Напишите Фамилию и Имя:\nПример: Юлдашев Нуриддин')
        bot.register_next_step_handler(msg, getName, phone)


def getName(message, phone):
    name = message.text
    createUser(message.chat.id, phone, name)
    bot.send_message(message.chat.id, "Вы успешно зарегестрировались!")


@bot.message_handler(content_types=['document'])
def get_doc(message):
    user = getUser(message.chat.id)
    if user[3]:
        file_id_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_id_info.file_path)
        with open("data.xlsx", "wb") as file:
            file.write(downloaded_file)
        helpers.create_files()
        users = getAllUsers()
        for u in users:
            try:
                with open(f'files/{u[1]}.xlsx', 'rb') as f:
                    bot.send_document(u[4], f)
            except Exception:
                pass


while True:
    try:
        bot.polling(none_stop=True, timeout=20)
    except Exception:
        bot.stop_bot()
        time.sleep(60)
