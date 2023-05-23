import sqlite3
class DatabaseModule:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
    
    def store_data(self, data, table_name):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS """ + table_name + "(id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT)")
        self.conn.commit()
        self.cursor.execute("""INSERT INTO """ + table_name + "(data)" , (data,))
        self.conn.commit()
    
    def retrieve_data(self, query, table_name):
        self.cursor.execute("""SELECT data FROM """ + table_name + "(data)" , ("%" + query + "%",))
        data = self.cursor.fetchall()
        return data
