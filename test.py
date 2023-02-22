
import sqlite3


conn = sqlite3.connect('client_connections.db')
c = conn.cursor()
c.execute('SELECT * FROM fichiers')
rows = c.fetchall() 

c.execute('SELECT COUNT(*) FROM emails')
ligne = c.fetchall() 
print(ligne[0])
for row in rows:
    print(row[2])