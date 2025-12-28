import sqlite3
import hashlib
import pandas as pd
from datetime import datetime

# Đường dẫn DB nằm trong folder data
DB_NAME = 'data/music_app.db'

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS ratings (username TEXT, track_id TEXT, rating INTEGER, PRIMARY KEY (username, track_id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS history (username TEXT, track_id TEXT, action_type TEXT, timestamp DATETIME)''')
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users(username, password) VALUES (?,?)', (username, make_hashes(password)))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username =? AND password = ?', (username, make_hashes(password)))
    data = c.fetchall()
    conn.close()
    return data

def add_rating(username, track_id, rating=5):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO ratings(username, track_id, rating) VALUES (?,?,?)', (username, track_id, rating))
    conn.commit()
    conn.close()

def remove_rating(username, track_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM ratings WHERE username = ? AND track_id = ?', (username, track_id))
    conn.commit()
    conn.close()

def log_interaction(username, track_id, action_type='view'):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO history(username, track_id, action_type, timestamp) VALUES (?,?,?,?)', 
              (username, track_id, action_type, datetime.now()))
    conn.commit()
    conn.close()

def get_last_interaction(username):
    conn = sqlite3.connect(DB_NAME)
    # Lấy bài hát mới nhất từ cả Rating và History
    query = f"""
        SELECT track_id, MAX(timestamp) as last_time FROM (
            SELECT track_id, '2025-01-01' as timestamp FROM ratings WHERE username = '{username}'
            UNION ALL
            SELECT track_id, timestamp FROM history WHERE username = '{username}'
        ) ORDER BY last_time DESC LIMIT 1
    """
    try:
        df = pd.read_sql_query(query, conn)
        return df.iloc[0]['track_id'] if not df.empty else None
    except:
        return None
    finally:
        conn.close()

def get_user_history_list(username):
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql_query(f"SELECT * FROM ratings WHERE username = '{username}'", conn)
    except:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df