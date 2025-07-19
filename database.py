import sqlite3

DATABASE_FILE = 'stocks.db'

def init_db():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL UNIQUE,
            condition_type TEXT NOT NULL,
            target_price REAL NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    print("בסיס הנתונים אותחל בהצלחה.")

if __name__ == '__main__':
    init_db()