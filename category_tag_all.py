from bs4 import BeautifulSoup
import mysql.connector
from aip import AipNlp
import re
from config import *
""" 你的 APPID AK SK """
APP_ID = '15606375'
API_KEY = 'bcBGUHh2vuSEbKMfbUGttbwx'
SECRET_KEY = 'BWfe4RCxslXheFthP9Gf5d8GGROGPyNT'

AIP_MAX_LEN_TITLE = 40 # 80/2
AIP_MAX_LEN_CONTENT = 30000 # 65535/2


client = AipNlp(APP_ID, API_KEY, SECRET_KEY)

# 注意把password设为你的root口令:
conn = mysql.connector.connect(user='root', password=sql_password, database='test')
conn.autocommit = True

cursor = conn.cursor()
cursor.execute("SELECT id, title, digest, content, link from entries where cate11 = \'\' order by id desc")
results = cursor.fetchall()
for result in results:
    entry_id = result[0]
    title = result[1].encode('gbk', 'ignore').decode('gbk')[0:AIP_MAX_LEN_TITLE]
    summary = result[2]
    content_html = result[3]
    link = result[4]
    if content_html and not link.startswith("https://weibo.com"):
        try:
            content = BeautifulSoup(content_html, "lxml").text.encode('gbk', 'ignore').decode('gbk')[0:AIP_MAX_LEN_CONTENT]
            if len(content) == 0:
                if len(summary) > 0:
                    content = summary
            keywords = client.keyword(title, content)
            topics = client.topic(title, content)
            cate1 = ['', '', '']
            cate2 = ['', '', '']
            tag = ['', '', '', '', '']
            i = 0
            for item in topics['item']['lv1_tag_list']:
                cate1[i] = item['tag']
                i += 1
                if i > 2:
                    break
            i = 0
            for item in topics['item']['lv2_tag_list']:
                cate2[i] = item['tag']
                i += 1
                if i > 2:
                    break
            i = 0
            for item in keywords['items']:
                tag[i] = item['tag']
                i += 1
                if i > 4:
                    break
            print(entry_id, title, cate1, cate2, tag)
            cursor.execute('update entries set cate11=%s, cate12=%s, cate13=%s, cate21=%s, cate22=%s, cate23=%s, tag1=%s, tag2=%s, tag3=%s, tag4=%s, tag5=%s where id = %s', 
                            tuple(cate1 + cate2 + tag + [entry_id]))
        except Exception as e:
            print('Exception when categorizing and tagging: {}, {}, {}'.format(entry_id, e, link))

conn.close()


