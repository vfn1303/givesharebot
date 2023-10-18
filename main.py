import uvicorn

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)
from telegram import ReplyKeyboardMarkup, KeyboardButton
import sqlite3
from dotenv import load_dotenv
import os



load_dotenv()

# ===================================================
# ====================== db =========================
# ===================================================
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()
# Добавление пользователя
def add_user(username, chat_id, subscribed):
    # проверяем есть ли юзер в боте
    cursor.execute("SELECT COUNT(*) FROM Users WHERE Chat_ID = ?", (int(chat_id),))
    result = cursor.fetchone()[0]

    if result == 0:
        query = "INSERT INTO Users (Username, Chat_ID, Subscribed) VALUES (?, ?, ?)"
        cursor.execute(query, (username, chat_id, subscribed))
        conn.commit()

def add_giveaway(name, desc, image, max, date):
    cursor.execute("INSERT INTO Giveaways (Giveaway_Name, Giveaway_Desc, Giveaway_Image, Max, End_Date) VALUES (?, ?, ?, ?, ?)", (name, desc, image, int(max), date))
    conn.commit()

# Получение всех пользователей
def get_all_users():
    cursor.execute("SELECT * FROM Users")
    return cursor.fetchall()

# все розыгрыши
def get_all_giveaways():
    cursor.execute("SELECT * FROM Giveaways")
    return cursor.fetchall()

# все участники розыгрыша
def get_participants(giveaway_id):
    query = """
    SELECT Users.Username
    FROM Giveaway_Participants
    JOIN Users ON Giveaway_Participants.User_ID = Users.ID
    WHERE Giveaway_Participants.Giveaway_ID = ?
    """
    cursor.execute(query, (giveaway_id,))
    participants = cursor.fetchall()
    
    return participants

def update_admin_status(username):
    query = "UPDATE Users SET Admin = ? WHERE Username = ?"
    cursor.execute(query, (1, username))
    conn.commit()

def update_max(max,id):
    query = "UPDATE Giveaways SET Max = ? WHERE ID = ?"
    cursor.execute(query, (max, id))
    conn.commit()

def update_date(date,id):
    query = "UPDATE Giveaways SET End_Date = ? WHERE ID = ?"
    cursor.execute(query, (date, id))
    conn.commit()

def update_image(image,id):
    query = "UPDATE Giveaways SET Giveaway_Image = ? WHERE ID = ?"
    cursor.execute(query, (image, id))
    conn.commit()

def update_text(text,id):
    query = "UPDATE Giveaways SET Giveaway_Desc = ? WHERE ID = ?"
    cursor.execute(query, (text, id))
    conn.commit()


def update_name(name,id):
    query = "UPDATE Giveaways SET Giveaway_Name = ? WHERE ID = ?"
    cursor.execute(query, (name, id))
    conn.commit()


def check_admin_status(chat_id):
    query = "SELECT Admin FROM Users WHERE Chat_ID = ?"
    cursor.execute(query, (chat_id,))
    result = cursor.fetchone()

    if result is not None and result[0] == 1:
        return True
    else:
        return False

def check_user_exists(username):
    query = "SELECT COUNT(*) FROM users WHERE Username = ?;"
    cursor.execute(query, (username,))

    result = cursor.fetchone()
    user_exists = result[0] > 0
    return user_exists

def get_giveaway_by_id(id):
    query = "SELECT COUNT(*) FROM users WHERE Username = ?;"
    cursor.execute(query, (id,))
    
    result = cursor.fetchone()
    user_exists = result[0] > 0
    return user_exists
# ===================================================
# ====================== db =========================
# ===================================================

#states
START, BEGIN_GIVEAWAY, DESCRIPTION, IMAGE, DATE, NUMBER, TEXT, CONFIRM= range(8)
CHOOSE_ADMIN, ADD_ADMIN, EDIT_ADMIN, CHOOSE_EDIT, NAME_ADMIN, IMAGE_ADMIN, TEXT_ADMIN, DATE_ADMIN, NUMBER_ADMIN, CONFIRM_ADMIN, BEGIN_NOW_ADMIN = range(11)

reply_keyboard = [['Отмена']]
cancel_markup = ReplyKeyboardMarkup(reply_keyboard)


def admin(update,context):
    user_id = update.message.from_user.id
    is_admin = check_admin_status(int(user_id))
    if is_admin:
        adm_keyboard = [['Вывести розыгрыши'],['Добавить админа'],['Отмена']]
        adm_markup = ReplyKeyboardMarkup(adm_keyboard)
        update.message.reply_text(
        'Вы вошли в админ панель.',
        reply_markup=adm_markup
        )
        return CHOOSE_ADMIN
    else:
        return ConversationHandler.END

def choose_admin(update,context):
    user_input = update.message.text
    
    if user_input == 'Отмена':
        cancel(update, context)
        return ConversationHandler.END
    if user_input == 'Добавить админа':
        update.message.reply_text('Отправьте ник админ без @.')
        return ADD_ADMIN
    if user_input == 'Вывести розыгрыши':
        print(str(get_all_giveaways()))

        choose_keyboard = [] #обавить все названия розыгрышей в формате [id:]назвние
        choose_markup = ReplyKeyboardMarkup(choose_keyboard)
        update.message.reply_text('Выберите нужный розыгрышь',reply_markup=choose_markup)
        return EDIT_ADMIN

def edit_admin(update,context):
    user_input = update.message.text
    context.user_data['giveaway_id'] = user_input #спарсить ид
    adm_keyboard = [[['Редактировать название'],['Редактировать описание'],['Редактировать изображение'],],
                    [['Редактировать дату'],['Редактировать кол-во участников'],['Начать досрочно']],
                    [['Отмена']]]
    adm_markup = ReplyKeyboardMarkup(adm_keyboard)
    update.message.reply_text(
    'что делать с розыгрышем',
    reply_markup=adm_markup
    )
    return CHOOSE_EDIT

def choose_edit(update,context):
    user_input = update.message.text
    if user_input == 'Редактировать название':
        update.message.reply_text('Отправьте новое название')
        return NAME_ADMIN
    elif user_input == 'Редактировать описание':
        update.message.reply_text('Отправьте новое описание')
        return TEXT_ADMIN
    elif user_input == 'Редактировать изобраение':
        update.message.reply_text('Отправьте новое изображение')
        return IMAGE_ADMIN
    elif user_input == 'Редактировать дату':
        update.message.reply_text('Отправьте новоую дату в формате дд мм гг час мин')
        return DATE_ADMIN
    elif user_input == 'Редактировать кол-во участников':
        update.message.reply_text('Отправьте новое количество участников')
        return NUMBER_ADMIN
    elif user_input == 'Начать досрочно':
        adm_keyboard = [['Да'],['Отмена']]
        adm_markup = ReplyKeyboardMarkup(adm_keyboard)
        update.message.reply_text('Вы хотите начать досрочно?', reply_markup = adm_keyboard)
        return CONFIRM_ADMIN
    else:
        cancel(update, context)
        return ConversationHandler.END


def name_admin(update,context):
    user_input = update.message.text
    update_name(user_input,context.user_data['giveaway_id'])
    update.message.reply_text('+')
    cancel(update, context)
    return ConversationHandler.END

def text_admin(update,context):
    user_input = update.message.text
    update_text(user_input,context.user_data['giveaway_id'])
    update.message.reply_text('+')
    cancel(update, context)
    return ConversationHandler.END



def image_admin(update,context):
    user_image = update.message.text

    update_image(user_image,context.user_data['giveaway_id'])

    update.message.reply_text("+")
    cancel(update, context)
    return ConversationHandler.END


def date_admin(update,context):
    user_input = update.message.text
    update_date(user_input,context.user_data['giveaway_id'])
    update.message.reply_text('+')
    cancel(update, context)
    return ConversationHandler.END


def number_admin(update,context):
    user_input = update.message.text
    if user_input.isdigit():
        update_max(int(user_input),context.user_data['giveaway_id'])
        update.message.reply_text('+')
        cancel(update, context)
        return ConversationHandler.END
    else:
        update.message.reply_text('ошибка введи число')
        return CONFIRM_ADMIN



def confirm_admin(update,context):
    #da net i zapustit
    user_input = update.message.text
    
    

def add_admin(update,context):
    user_input = update.message.text
    if check_user_exists(user_input):
        add_admin(user_input)
        update.message.reply_text('Админ добавлен')
        return ConversationHandler.END
    else:
        update.message.reply_text('Такого пользователя нет в боте')
        return CHOOSE_ADMIN

def start(update, context):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.username
    add_user(user_name, user_id,0)
    keyboard = [['посмотреть розыгрыши']]
    markup = ReplyKeyboardMarkup(keyboard)
    # Обработка параметров
    params = context.args
    if len(params) > 0:
        update.message.reply_text(get_giveaway_by_id(params))
        
    else:
        update.message.reply_text('текст главного меню',reply_markup=markup)



def create_giveaway(update, context):
    user_id = update.message.from_user.id
    is_admin = check_admin_status(int(user_id))
    if is_admin:
        update.message.reply_text(
        'Привет админ. введи название розыгрыша'
        )
        return BEGIN_GIVEAWAY
    else:

    # показать розыгрышь по рефералке или показать все доступные розыгрыши 
    # 1 выбрать розыгрышь 
    # 2 выдать юзеру код
        pass

def begin_giveaway(update, context):
    reply_keyboard = [['Отмена']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    
    update.message.reply_text(
        'Введите название розыгрыша.',
        reply_markup=markup
    )
    
    return DESCRIPTION

def description(update, context):
    user_input = update.message.text
    
    if user_input == 'Отмена':
        cancel(update, context)
        return ConversationHandler.END
    
    context.user_data['description'] = user_input
    
    update.message.reply_text('Отлично! Теперь отправь мне ссылку картинку.',reply_markup=cancel_markup)
    
    return IMAGE

def image(update, context):

    user_image = update.message.text

    if user_image == 'Отмена':
        cancel(update, context)
        return ConversationHandler.END
    
    context.user_data['image'] = user_image

    update.message.reply_text("Хорошо. Теперь введи дату в формате дд мм гг час мин",reply_markup=cancel_markup)
    
    return DATE

def date(update, context):

    user_date = update.message.text
    
    if user_date == 'Отмена':
        cancel(update, context)
        return ConversationHandler.END
    
    context.user_data['date'] = user_date
    
    update.message.reply_text('Отлично! Теперь введи максимальное число участников.',reply_markup=cancel_markup)
    
    return NUMBER

def number(update, context):
    user_number = update.message.text
    
    if user_number == 'Отмена':
        cancel(update, context)
        return ConversationHandler.END
    
    context.user_data['number'] = user_number
    
    update.message.reply_text('Хорошо. Теперь введи текст для розыгрыша.',reply_markup=cancel_markup)
    
    return TEXT

def text(update, context):
    user_text = update.message.text
    
    reply_keyboard = [['Сохранить'],['Отмена']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    if user_text == 'Отмена':
        cancel(update, context)
        return ConversationHandler.END
    
    context.user_data['text'] = user_text
    
    confirmation_message = f'Подтверждение:\n Описание: {context.user_data["description"]}\n Картинка: {context.user_data["image"]}\n Дата: {context.user_data["date"]}\n Число участников: {context.user_data["number"]}\n Текст: {context.user_data["text"]}'

    
    update.message.reply_text(confirmation_message,reply_markup=markup,disable_web_page_preview=False)

    return ConversationHandler.END

def confirm(update, context):
    user_text = update.message.text

    if user_text == 'Сохранить':
        #base
        add_giveaway(context.user_data["description"],context.user_data["text"],context.user_data["image"],int(context.user_data["number"]),context.user_data["date"])

        update.message.reply_text('все в базе')
        #в крон
        #TODO
        return ConversationHandler.END
    elif user_text == 'Отмена':
        cancel(update, context)
        return ConversationHandler.END
    else:
        return TEXT

    

def cancel(update, context):
    update.message.reply_text('Действие отменено.')
    #сюда главное меню пихнуть
    return ConversationHandler.END

def main():
    # Запросы на создание таблиц (если они не существуют)
    create_users_table = """CREATE TABLE IF NOT EXISTS Users (
        ID INT PRIMARY KEY,
        Username VARCHAR(255),
        Chat_ID INT,
        Subscribed BIT,
        Admin BIT DEFAULT 0 
    );"""

    create_giveaways_table = """CREATE TABLE IF NOT EXISTS Giveaways (
        ID INT PRIMARY KEY,
        Giveaway_Name VARCHAR(255),
        Giveaway_Desc VARCHAR(255),
        Giveaway_Image VARCHAR(255),
        Max INT,
        End_Date VARCHAR(255),
        Winner INT DEFAULT 0 
    );"""

    create_giveaway_participants_table = """CREATE TABLE IF NOT EXISTS Giveaway_Participants (
        ID INT PRIMARY KEY,
        User_ID INT,
        Giveaway_ID INT,
        FOREIGN KEY (User_ID) REFERENCES Users(ID),
        FOREIGN KEY (Giveaway_ID) REFERENCES Giveaways(ID)
    );"""

    cursor.execute(create_users_table)
    cursor.execute(create_giveaways_table)
    cursor.execute(create_giveaway_participants_table)

    updater = Updater(os.getenv('TOKEN'), use_context=True)
    dp = updater.dispatcher
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('create_giveaway', create_giveaway)],
        states={
            BEGIN_GIVEAWAY: [MessageHandler(Filters.text, begin_giveaway)],
            DESCRIPTION: [MessageHandler(Filters.text, description)],
            IMAGE: [MessageHandler(Filters.text, image)],
            DATE: [MessageHandler(Filters.text, date)],
            NUMBER: [MessageHandler(Filters.text, number)],
            TEXT: [MessageHandler(Filters.text, text)],
            CONFIRM: [MessageHandler(Filters.text, confirm)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dp.add_handler(conv_handler)

    adm_handler = ConversationHandler(
        entry_points=[CommandHandler('admin', admin)],
        states={
            CHOOSE_ADMIN: [MessageHandler(Filters.text, choose_admin)],
            EDIT_ADMIN: [MessageHandler(Filters.text, edit_admin)],
            IMAGE_ADMIN: [MessageHandler(Filters.text, image_admin)],
            TEXT_ADMIN: [MessageHandler(Filters.text, text_admin)],
            NAME_ADMIN: [MessageHandler(Filters.text, name_admin)],
            DATE_ADMIN: [MessageHandler(Filters.text, date_admin)],
            NUMBER_ADMIN: [MessageHandler(Filters.text, number_admin)],
            CONFIRM_ADMIN: [MessageHandler(Filters.text, confirm_admin)],
            BEGIN_NOW_ADMIN: [MessageHandler(Filters.text, begin_giveaway)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dp.add_handler(adm_handler)
    SHOW_GIVEAWAYS, ENTER_GIVEAWAY = range(2)
    start_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SHOW_GIVEAWAYS: [MessageHandler(Filters.text, text)],
            ENTER_GIVEAWAY: [MessageHandler(Filters.text, text)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dp.add_handler(start_handler)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    uvicorn.run("main:main", host="0.0.0.0", port=8081, reload=True)