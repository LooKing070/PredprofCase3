import sqlite3
import os

try:
    os.remove("sql_bd.db")
except Exception as error:
    print(error)

conn = sqlite3.connect("sql_bd.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE files
                  (name TEXT,
                  content TEXT)''')
conn.commit()
conn.close()
