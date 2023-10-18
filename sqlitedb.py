import sqlite3

# Создать подключение к базе данных
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Запросы на создание таблиц (если они не существуют)
create_users_table = """CREATE TABLE Users (
    ID INT PRIMARY KEY,
    Username VARCHAR(255),
    Chat_ID INT,
    Subscribed BIT,
    Admin BIT
);"""

create_giveaways_table = """CREATE TABLE Giveaways (
    ID INT PRIMARY KEY,
    Giveaway_Name VARCHAR(255),
    Giveaway_Desc VARCHAR(255),
    Giveaway_Image VARCHAR(255),
    Max INT,
    End_Date DATE
);"""

create_giveaway_participants_table = """CREATE TABLE Giveaway_Participants (
    ID INT PRIMARY KEY,
    User_ID INT,
    Giveaway_ID INT,
    FOREIGN KEY (User_ID) REFERENCES Users(ID),
    FOREIGN KEY (Giveaway_ID) REFERENCES Giveaways(ID)
);"""


cursor.execute(create_users_table)
cursor.execute(create_giveaways_table)
cursor.execute(create_giveaway_participants_table)
# Добавление пользователя
def add_user(name, id,is_subbed,is_admin):
    cursor.execute("INSERT INTO Users (name, id,subbed, admin) VALUES (?, ?, ?, ?)", (name, id, is_subbed, is_admin))
    conn.commit()

def add_giveaway(name, desc, image, max, date):
    cursor.execute("INSERT INTO Giveaways (name, desc, image, max, date) VALUES (?, ?, ?, ?, ?)", (name, desc, image, max, date))
    conn.commit()

def add_giveaway(user_id, giveaway_id):
    cursor.execute("INSERT INTO Giveaway_Participants (user_id, giveaway_id) VALUES (?, ?)", (user_id, giveaway_id))

# Получение всех пользователей
def get_all_users():
    cursor.execute("SELECT * FROM Users")
    return cursor.fetchall()

def get_all_giveaways():
    cursor.execute("SELECT * FROM Giveaways")
    return cursor.fetchall()
