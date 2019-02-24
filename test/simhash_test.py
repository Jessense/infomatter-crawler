import re
from simhash import Simhash, SimhashIndex
import jieba
import requests
import json
import ast
import time
from sumy.utils import get_stop_words
import nltk


tolerance = 13  # 容忍度，判断是不是相似用的





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
    punc = list('`~!@#$%^&*()_+-={}|:\"<>?[]\\;\',./')
    s = s.lower()
    s = nltk.word_tokenize(s)
    for word in s:
        if word in get_stop_words('english') or word in punc:
            s.remove(word)
    return s

def get_features_cn(s):
    punc = list('·~！!@#￥$%…&*（）()_——+-={}|、：:\'\"\\“”《》<>？?【】[]；‘’，。,./')
    s = s.lower()
    s = (" ".join(jieba.cut(s))).split()
    for word in s:
        if word in get_stop_words('chinese') or word in punc:
            s.remove(word)
    return s

def clustering():
    fout = open('cluster.txt', 'w', encoding='UTF-8')
    response = requests.get('http://188.131.178.76:3000/entries/cluster/1000')
    response_text = response.text
    entrylist = ast.literal_eval(response_text)


    objs = []
    entrydic = {}
    for item in entrylist:
        if not is_en(item['title']):
            if not item['link'].startswith("https://weibo.com"):
                sim = Simhash(get_features_cn(item['title']))
                objs.append((str(item['id']), sim))
                entrydic[str(item['id'])] = {
                    'title': item['title'],
                    'cluster': 0,
                    'sim_count': 0,
                    'link': item['link'],
                    'simhash': sim.value
                }
        else:
            sim = Simhash(get_features(item['title']))
            objs.append((str(item['id']), sim))
            entrydic[str(item['id'])] = {
                'title': item['title'],
                'cluster': 0,
                'sim_count': 0,
                'link': item['link'],
                'simhash': sim.value
            }


    index = SimhashIndex(objs, k=tolerance)
    cluster_num = 1
    for key in entrydic:
        if entrydic[key]['cluster'] == 0:
            sims = index.get_near_dups(Simhash(get_features_cn(entrydic[key]['title'])))
            for item in sims:
                entrydic[item]['cluster'] = cluster_num
                if len(sims) > 1:
                    entrydic[item]['sim_count'] = len(sims) - 1
                    fout.write(item + '\t' + str(entrydic[item]['cluster']) + '\t' + entrydic[item]['title'] + '\t' + entrydic[item]['link'] + '\n')
            cluster_num += 1

    # print("--------------------------------------")
    # for key in entrydic:
    #     print(key + '\t' + str(entrydic[key]['cluster']) + '\t' + entrydic[key]['title'])



clustering()

