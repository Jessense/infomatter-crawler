# 微博输出uid --君智 2019.5.2
# zwf 2019-5-13 修复了uid和uname的bug
import re
from bs4 import BeautifulSoup
import requests
import json

import re
from bs4 import BeautifulSoup
import requests
import json


def weibo(keyword):
    response = requests.get('https://s.weibo.com/user?q='+keyword +
                            '&Refer=weibo_user&sudaref=s.weibo.com&display=0&retcode=6102')
    html = response.text
    soup = BeautifulSoup(html, "lxml")
    imgs = soup.select(".avator")
    uids = soup.select(".s-btn-c")
    names = soup.select(".name")
    resultuid = []
    resultuname = []
    resultimg = []

    for i in imgs:
        b = i.a.prettify()

        matchimg = re.search(r'img src="(.+?)"', b)
        img = matchimg.group(1)
        resultimg.append(img)

    for i in uids:
        resultuid.append(i.attrs['uid'])

    for i in names:
        uname = ''
        for j, children in enumerate(i.children):
            uname += children.string
        resultuname.append(uname)

    # store
    python2json = {}
    json_str = ''
    i = 0
    while i < len(resultuid):
        python2json['id'] = 999999 + i
        # python2json["uid"] = resultuid[i]
        python2json["name"] = resultuname[i] + '的微博'
        python2json['feedUrl'] = 'http://127.0.0.1:1200/weibo/user/' + resultuid[i]
        python2json['link'] = 'https://weibo.com/u/' + resultuid[i]
        python2json["photo"] = 'https:' + resultimg[i]
        python2json['category'] = 'E'
        python2json['form'] = 2
        python2json['content_rss'] = 1
        if i < len(resultuid) - 1:
            json_str += json.dumps(python2json) + ','
        else:
            json_str += json.dumps(python2json)
        i += 1
    json_str = '[' + json_str + ']'

    return json_str


if __name__ == "__main__":
    keyword = 'qq'
    result = weibo(keyword)
    print(result)
