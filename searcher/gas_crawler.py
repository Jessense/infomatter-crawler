# 2019-5-18 zwf 爬瓦斯阅读

from bs4 import BeautifulSoup
import requests
import json
import re

def wechat_wasi(keyword):
    response = requests.get("https://wx.qnmlgb.tech/search?q=" + keyword)
    html = response.text
    soup = BeautifulSoup(html, "lxml")
    # 找名字，个性签名，图片链接，还有RSS链接
    names = soup.select(".ae-author")
    describes = soup.select(".pretty")
    imgs = soup.select(".ae-profile-img")
    rss = soup.select(".ae")
    name_list = []
    describe_list = []
    img_list = []
    rss_list = []
    # 找名字
    for item in names:
        name = ''
        for j, children in enumerate(item.children):
            name += children.string
        name_list.append(name.strip())
    # 个性签名
    for item in describes:
        describe = ''
        for j, children in enumerate(item.children):
            describe += children.string
        describe_list.append(describe)
    # 图片链接
    for item in imgs:
        img_list.append(item.get("src"))
    # RSS
    for item in rss:
        matchimg = re.search(r'/authors/(.*)', str(item.get("href")))
        if matchimg != None:
            rss_list.append("https://q.qnmlgb.tech/w/rss/" + matchimg.group(1))
        else:
            print("Error happend when extracting rss link!")
    # 保存
    python2json = {}
    json_str = ''
    i = 0
    while i < len(name_list):
        python2json['id'] = 999999 + i
        python2json["name"] = name_list[i] + "公众号"
        python2json["description"] = describe_list[i]
        python2json["photo"] = 'https://weixin.qq.com/zh_CN/htmledition/images/wechat_logo_109.2x219536.png'
        python2json["feedUrl"] = rss_list[i]
        python2json["link"] = rss_list[i]
        python2json['category'] = '4'
        python2json['form'] = 1
        python2json['content_rss'] = 3
        if i < len(name_list) - 1:
            json_str += json.dumps(python2json) + ','
        else:
            json_str += json.dumps(python2json)
        i += 1
    json_str = '[' + json_str + ']'

    return json_str

if __name__ == "__main__":
    keyword = 'qq'
    result = wechat_wasi(keyword)
    print(result)
