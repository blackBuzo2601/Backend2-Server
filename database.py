import sqlite3
from config import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH)

def check_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user=? AND password=?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result

def user_exists(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE user=?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def create_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (user, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()
