# coding = unicode_escape
# 遇到知乎400报，添加头伪装浏览器之后能够抓到页面
# 同时用添加头的方式躲过了搜狗封ip
# 2019-5-22 zwf 1.1版本
# 减少了获取的用户数目，提高速度，感觉还可以
import re
from bs4 import BeautifulSoup
import requests
import json
import datetime
# 这个函数有点坑爹，没用，我看response.text输出有问题才写的，写完看json没有问题，真是艹了
def unicode2utf8(str):
    result = ''
    i = 0
    while i < len(str):
        c = str[i]
        if str[i] == '\\' and str[i+1] == 'u':
            c = str[i]+str[i+1]+str[i+2]+str[i+3]+str[i+4]+str[i+5]
            c = c.encode().decode("unicode_escape")
            i += 5
        result += c
        i += 1
    return result


def zhihu_crawler(keyword):
    # 设计头模仿浏览器
    headers = {
        # 'referer': 'https://www.zhihu.com/search?type=people&q='+keyword,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
    }
    # 第一轮捕获
    url = 'https://www.zhihu.com/api/v4/search_v3?t=people&correction=1&limit=20&lc_idx=0&show_all_topics=0&q='+keyword
    response = requests.get(url, headers = headers)
    data = response.json()
    result = []
    # name, img, id, description
    i = 0
    for entry in data["data"]:
        user = dict()
        user["id"] = 999999 + i
        user["name"] = entry["object"]["name"].replace("<em>","").replace("</em>","") + "的知乎动态"
        # id有点不确定
        user["feedUrl"] = "http://127.0.0.1:1200/zhihu/people/activities/" + entry["object"]["url_token"]
        user["link"] = "https://www.zhihu.com/people/diygod/" + entry["object"]["url_token"] + "/activities"
        user["photo"] = entry["object"]["avatar_url"]
        user["description"] = entry["object"]["headline"]
        user["category"] = "Z"
        user["form"] = 1
        user["content_rss"] = 1
        result.append(user)
        i += 1
    return json.dumps(result)


if __name__ == "__main__":
    keyword = '海贼王'
    begin = datetime.datetime.now()
    result = zhihu_crawler(keyword)  # 注意返回的是列表
    # print("用时", datetime.datetime.now() - begin)

    # print(result.__len__())
    # print(result[result.__len__()-1])
    # 爬了207个，比网页上刷出来的还多。。。。
