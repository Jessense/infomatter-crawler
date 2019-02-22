import re
from simhash import Simhash, SimhashIndex
import jieba
import requests
import json
import ast
import time



tolerance = 15  # 容忍度，判断是不是相似用的





# ****************停用词库
file = open('./stopwords.txt', 'r', encoding='UTF-8')
lines = file.readlines()

stopwords = set()
# print(lines)
for line in lines:
    word = ''
    for letter in line:
        if (letter != '\ufeff') and (letter != ' ') and (letter != '\n'):
            word += letter
    stopwords.add(word)
# print(stopwords)
# **************************************************

def is_en(s):
    for uchar in s:
        if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
            return False
    return True


def is_cn(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

def get_features(s):
    width = 3
    s = s.lower()
    s = re.sub(r'[^\w]+', '', s)
    return [s[i:i + width] for i in range(max(len(s) - width + 1, 1))]


def get_features_cn(s):
    s = s.lower()
    s = re.sub(r'[^\w]+', '', s)
    s = (" ".join(jieba.cut(s))).split()
    for word in s:
        if word in stopwords:
            s.remove(word)
    return s

def clustering():
    fout = open('cluster.txt', 'w', encoding='UTF-8')
    response = requests.get('http://188.131.178.76:3000/entries/cluster/5000')
    response_text = response.text
    entrylist = ast.literal_eval(response_text)
    # entrylist = [
    #     {'id': 1, 'title': u'How are you? I Am fine. blar blar blar blar blar Thanks.', 'cluster': 0, 'isclustered': False},
    #     {'id': 2, 'title': u'How are you i am fine. blar blar blar blar blar than', 'cluster': 0, 'isclustered': False},
    #     {'id': 3, 'title': u'This is simhash test.', 'cluster': 0, 'isclustered': False},
    # ]

    objs = []
    entrydic = {}
    for item in entrylist:
        if not is_en(item['title']) and not item['link'].startswith("https://weibo.com"):
            entrydic[str(item['id'])] = {
                'title': item['title'],
                'cluster': 0,
                'sim_count': 0,
                'link': item['link']
            }
            objs.append((str(item['id']), Simhash(get_features_cn(item['title']))))

    index = SimhashIndex(objs, k=tolerance)
    cluster_num = 1
    for key in entrydic:
        if entrydic[key]['cluster'] == 0:
            sims = index.get_near_dups(Simhash(get_features_cn(entrydic[key]['title'])))
            for item in sims:
                entrydic[item]['cluster'] = cluster_num
                if len(sims) > 1:
                    fout.write(item + '\t' + str(entrydic[item]['cluster']) + '\t' + entrydic[item]['title'] + '\t' + entrydic[item]['link'] + '\n')
            cluster_num += 1

    # print("--------------------------------------")
    # for key in entrydic:
    #     print(key + '\t' + str(entrydic[key]['cluster']) + '\t' + entrydic[key]['title'])



clustering()

