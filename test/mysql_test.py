import mysql.connector
# 注意把password设为你的root口令:
conn = mysql.connector.connect(user='root', password='123456', database='test')

cursor = conn.cursor()
cursor.execute("INSERT INTO readed (user_id, entry_id) VALUES (1, 1)")
print(cursor.lastrowid)
conn.commit()
conn.close()