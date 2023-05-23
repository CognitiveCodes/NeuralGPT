import sqlite3

class Memory:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS short_term_memory
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            data TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS long_term_memory
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            data TEXT)''')
        self.conn.commit()

    def add_to_short_term_memory(self, data):
        self.cursor.execute("INSERT INTO short_term_memory (data) VALUES (?)", (data,))
        self.conn.commit()

    def add_to_long_term_memory(self, data):
        self.cursor.execute("INSERT INTO long_term_memory (data) VALUES (?)", (data,))
        self.conn.commit()

    def retrieve_from_short_term_memory(self):
        self.cursor.execute("SELECT * FROM short_term_memory")
        return self.cursor.fetchall()

    def retrieve_from_long_term_memory(self):
        self.cursor.execute("SELECT * FROM long_term_memory")
        return self.cursor.fetchall()

    def clear_short_term_memory(self):
        self.cursor.execute("DELETE FROM short_term_memory")
        self.conn.commit()

    def clear_long_term_memory(self):
        self.cursor.execute("DELETE FROM long_term_memory")
        self.conn.commit()