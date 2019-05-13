# 微博输出uid --君智 2019.5.2
import re
from bs4 import BeautifulSoup
import requests
import json

keyword = '科技美学'
response = requests.get('https://s.weibo.com/user?q='+keyword +
                        '&Refer=weibo_user&sudaref=s.weibo.com&display=0&retcode=6102')
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

python2json = {}
json_str = ''
for i in range(0, len(resultuid)):
    python2json["uid"] = resultuid[i]
    python2json["uname"] = resultuname[i]
    python2json["photo"] = resultimg[i]
    json_str = json.dumps(python2json) + ',' + json_str

json_str = '[' + json_str + ']'
#print(python2json)
print(json_str)

'''
b=soup.select(".avator")
#print(b)
length = len(b)
print(length)
for i in b:
    print(i)
pattern = re.compile(r'\d+')                    # 用于匹配至少一个数字

c = [a.attrs.get('href') for a in b]
print(c)
'''
'''
for i in b:
    str4 = "".join(i)
    print(i)
    m = pattern.match(i)
    print(m)
##for tag in soup.find_all(re.compile("t")):
##    print(tag.name)
##print(a)
'''
