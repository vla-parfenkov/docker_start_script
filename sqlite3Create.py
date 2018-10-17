import sqlite3

conn = sqlite3.connect("idApp.db") 
cursor = conn.cursor()
 
cursor.execute("""CREATE TABLE Apps (id text, port int, container text)""")