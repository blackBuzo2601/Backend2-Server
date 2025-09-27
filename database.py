import sqlite3
from config import DB_PATH

def get_connection():
    # cada hilo pedirá su propia conexión
    return sqlite3.connect(DB_PATH)

def check_user(username, password):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM users WHERE user=? AND password=?", (username, password))
        row = cur.fetchone()
        conn.close()
        return row is not None
    except Exception:
        return False

def user_exists(username):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM users WHERE user=?", (username,))
        row = cur.fetchone()
        conn.close()
        return row is not None
    except Exception:
        return False

def create_user(username, password):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (user, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return True, None
    except sqlite3.IntegrityError as e:
        return False, "IntegrityError"
    except Exception as e:
        return False, str(e)
