import sqlite3

def init_db():
    conn = sqlite3.connect('medicines.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def insert_medicine(name):
    conn = sqlite3.connect('medicines.db')
    c = conn.cursor()
    c.execute('INSERT INTO medicines (name) VALUES (?)', (name,))
    conn.commit()
    conn.close()