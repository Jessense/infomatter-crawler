from flask import Flask, Response
from flask import request
import re
from bs4 import BeautifulSoup
import requests
import json

app = Flask(__name__)


def weibo_search(keyword):
    response = requests.get('https://s.weibo.com/user?q='+keyword +
                            '&Refer=weibo_user')
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select(".avator")
    itemsname = soup.select(".name")
    pattern1 = re.compile(r'\d+')
    resultuid = []
    resultuname = []
    resultimg = []
    pattern2 = re.compile(u"([\u4e00-\u9fff]+)")

    #print(items)

    for i in items:
        b = i.a.prettify()
        #print(b)
        #print(type(b))
        uid = b[21:50]
        #print(uid)
        if uid[0] == "u":
            uid = uid[2:]
        str = ''
        for temp in range(0, len(uid)):
            if uid[temp] != "\"":
                str = str + uid[temp]
            else:
                break
        resultuid.append(str)

        matchimg = re.search(r'img src="(.+?)"', b)
        img = matchimg.group(1)
        resultimg.append(img)
    '''   if matchimg :
            print(img)
        else :
            print("no img")
    '''

    for i in itemsname:
        str = i.prettify()
        s = pattern2.findall(str)
        uname = ''
        for j in s:
            uname = uname + j
        resultuname.append(uname)

    #print(resultuid)
    #print(resultuname)
    #print(resultimg)

    source = {}
    source_list = ''
    # for i in range(0, len(resultuid)):
    i = 0
    while i < len(resultuid):
        source['id'] = 999999
        # source["uid"] = resultuid[i]
        source["name"] = resultuname[i]
        source['feedUrl'] = 'http://127.0.0.1.55:1200/weibo/user/' + resultuid[i]
        source['link'] = 'https://weibo.com/u/' + resultuid[i]
        source["photo"] = 'https:' + resultimg[i]
        source['category'] = 'E'
        source['form'] = 2
        source['content_rss'] = 1
        if i < len(resultuid) - 1:
	        source_list += json.dumps(source) + ','
        else:
            source_list += json.dumps(source)
        i += 1

    source_list = '[' + source_list + ']'
    return source_list

@app.route('/')
def hello_world():
    return 'Hello World!'



@app.route('/weibo', methods=['GET'])
def search():
    error = None
    if request.method == 'GET':
        keyword = request.args.get('keyword', '')
        return Response(weibo_search(keyword), mimetype='application/json')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
