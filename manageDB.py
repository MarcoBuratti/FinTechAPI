import sqlite3

def dbConnection():
    conn = None
    try:
        conn = sqlite3.connect('FINTECH.sqlite', check_same_thread=False)
    except sqlite3.error as e:
        print(e)
    return conn