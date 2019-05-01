import mysql.connector
# 注意把password设为你的root口令:
conn = mysql.connector.connect(user='root', password='123456', database='test_school')

cursor = conn.cursor()
cursor.execute(
    "INSERT INTO fuck (id, name) VALUES (\"10\", \"哈哈\")")
conn.commit()
print(cursor.fetchone())
conn.close()
