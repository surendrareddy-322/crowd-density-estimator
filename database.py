import sqlite3
from datetime import datetime
import pandas as pd

DB_NAME = 'crowd_data.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS crowd_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            zone_count INTEGER,
            total_detected INTEGER,
            risk_level TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_detection(zone_count, total_detected, risk_level):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO crowd_logs (zone_count, total_detected, risk_level)
        VALUES (?, ?, ?)
    ''', (zone_count, total_detected, risk_level))
    conn.commit()
    conn.close()

def get_historical_data():
    conn = sqlite3.connect(DB_NAME)
    # Read into a pandas DataFrame for easy plotting in Streamlit
    df = pd.read_sql_query("SELECT * FROM crowd_logs", conn)
    conn.close()
    if not df.empty:
        # Convert timestamp string to datetime object
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df
