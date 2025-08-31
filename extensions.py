from __init__ import mysql

cursor = mysql.connection.cursor()
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()
for row in rows:
    print(row)
cursor.close()
