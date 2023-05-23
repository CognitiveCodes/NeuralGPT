import sqlite3

class MemoryModule:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()
        
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS short_term_memory 
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                          data TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS long_term_memory 
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                          data TEXT)''')
        self.conn.commit()
        
    def store_data(self, data, memory_type):
        cursor = self.conn.cursor()
        if memory_type == 'short_term':
            cursor.execute('''INSERT INTO short_term_memory (data) VALUES (?)''', (data,))
        elif memory_type == 'long_term':
            cursor.execute('''INSERT INTO long_term_memory (data) VALUES (?)''', (data,))
        self.conn.commit()
        
    def retrieve_data(self, query, memory_type):
        cursor = self.conn.cursor()
        if memory_type == 'short_term':
            cursor.execute('''SELECT data FROM short_term_memory WHERE data LIKE ?''', ('%' + query + '%',))
        elif memory_type == 'long_term':
            cursor.execute('''SELECT data FROM long_term_memory WHERE data LIKE ?''', ('%' + query + '%',))
        data = cursor.fetchall()
        return data