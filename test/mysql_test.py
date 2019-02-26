import mysql.connector
# 注意把password设为你的root口令:
conn = mysql.connector.connect(user='root', password='123456', database='test')

cursor = conn.cursor()
cursor.execute(
    "SELECT id, title, cate11, cate21, tag1 from entries order by id desc limit 3")
# conn.commit()
# cursor.execute('select id, title, category from entries where id = 200')
print(cursor.fetchone())
conn.close()
