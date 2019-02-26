from aip import AipNlp
import re

""" 你的 APPID AK SK """
APP_ID = '15606375'
API_KEY = 'bcBGUHh2vuSEbKMfbUGttbwx'
SECRET_KEY = 'BWfe4RCxslXheFthP9Gf5d8GGROGPyNT'


client = AipNlp(APP_ID, API_KEY, SECRET_KEY)

title = "iphone手机出现“白苹果”原因及解决办法，用苹果手机的可以看下"

content = "如果下面的方法还是没有解决你的问题建议来我们门店看下成都市锦江区红星路三段99号银石广场24层01室。"

""" 调用文章标签 """
client.keyword(title, content)
