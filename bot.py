import telebot
import helpers
import time
import mysql.connector
from mysql.connector import errorcode
import sys
from time import sleep

API_TOKEN = '1725219040:AAGFuicW0cXzJXVLLJK1qVJxO_1uBElU2Vk'

bot = telebot.TeleBot(API_TOKEN)


def getContactMarkup():
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add(telebot.types.KeyboardButton('Отправить свой номер', request_contact=True))
    return markup

def getConnection():
    try:
        db = mysql.connector.connect(
            host="193.23.127.34",
            user="desmond",
            passwd="Agent007!",
            port="3306",
            database="cepla"
        )
        return db
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        sleep(60)
        getConnection()



def getUser(chat_id):
    db = getConnection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE chat_id = %s", (chat_id, ))
    result = cursor.fetchone()
    return result


def getAllUsers():
    db = getConnection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users")
    result = cursor.fetchall()
    return result


def createUser(chat_id, phone, name):
    db = getConnection()
    cursor = db.cursor()
    cursor.execute("INSERT INTO users (chat_id, phone, draft) VALUES (%s , %s, %s)", (chat_id, phone, name))
    db.commit()


@bot.message_handler(commands=['start'])
def command_start(message):
    if getUser(message.chat.id) is None:
        bot.send_message(message.chat.id, 'Пожалуйста отправьте свой номер(Кликните по кнопке снизу!)', reply_markup=getContactMarkup())


@bot.message_handler(content_types=['contact'])
def contact(message):
    print(message.contact)
    if message.contact is not None and getUser(message.chat.id) is None:
        phone = message.contact.phone_number
        msg = bot.send_message(message.chat.id, 'Напишите Фамилию и Имя:\nПример: Юлдашев Нуриддин', reply_markup=telebot.types.ReplyKeyboardRemove())
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


bot.polling()
