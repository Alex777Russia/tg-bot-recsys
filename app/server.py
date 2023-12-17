import sqlite3

def create_db():
    connection = sqlite3.connect('bot_history.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            first_name TEXT NOT NULL,
            chat_id TEXT NOT NULL,
            message TEXT NOT NULL,
            date TEXT NOT NULL
        );
    ''')
    connection.commit()
    cursor.close()
    connection.close()


def insert_message(user_id, first_name, chat_id, message, date):
    connection = sqlite3.connect('bot_history.db')
    cursor = connection.cursor()
    cursor.execute("INSERT INTO messages VALUES (NULL, ?, ?, ?, ?, ?)", (user_id, first_name, chat_id, message, date))
    connection.commit()
    cursor.close()
    connection.close()