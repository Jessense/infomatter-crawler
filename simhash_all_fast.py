import re
from simhash import Simhash, SimhashIndex
import jieba.analyse
import requests
import json
import ast
import time
import mysql.connector
from sumy.utils import get_stop_words
import nltk
from bs4 import BeautifulSoup
from config import *
# 注意把password设为你的root口令:
conn = mysql.connector.connect(
    user='root', password=sql_password, database='test')
conn.autocommit = True  # 重要！


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


# def get_features(s):
#     punc = list('`~!@#$%^&*()_+-={}|:\"<>?[]\\;\',./')
#     s = s.lower()
#     s = nltk.word_tokenize(s)
#     for word in s:
#         if word in get_stop_words('english') or word in punc:
#             s.remove(word)
#     return s

def get_features(title, content):
    title_tags = jieba.analyse.extract_tags(title, topK=10, withWeight=True)
    content_tags = jieba.analyse.extract_tags(
        BeautifulSoup(content, "lxml").text, topK=10, withWeight=True)
    tags = {}
    for k, v in title_tags:
        tags[k] = v
    for k, v in content_tags:
        if k in tags:
            tags[k] = tags[k] + v
        else:
            tags[k] = v
    return tags

# def get_features_cn(s):
#     punc = list('·~！!@#￥$%…&*（）()_——+-={}|、：:\'\"\\“”《》<>？?【】[]；‘’，。,./')
#     s = s.lower()
#     s = (" ".join(jieba.cut(s))).split()
#     for word in s:
#         if word in get_stop_words('chinese') or word in punc:
#             s.remove(word)
#     return s


cluster_num = 0
objs = []
index = SimhashIndex(objs, k=tolerance)


def restore_simhash():
    global cluster_num
    print('restoring...')
    cursor = conn.cursor()
    cursor.execute('select id, simhash from entries where simhash > 0')
    entries = cursor.fetchall()
    for entry in entries:
        index.add(str(entry[0]), Simhash(int(entry[1])))

    cursor.execute('select max(cluster) from entries')
    cluster_num = cursor.fetchone()[0] + 1

def update_simhash():
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, title, content, cluster, sim_count, link, simhash FROM entries where cluster = 0')
    entrylist = cursor.fetchall()
    for item in entrylist:
        features = get_features(item[1], item[2])
        sim = Simhash(features)

        cursor.execute('UPDATE entries SET simhash=%s where id = %s', (
            str(sim.value), item[0]))

def clustering():
    global index
    global cluster_num
    # fout = open('cluster.txt', 'w', encoding='UTF-8')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, title, content, cluster, sim_count, link, simhash FROM entries where cluster = 0')
    entrylist = cursor.fetchall()
    for item in entrylist:
        print(item[0])
        sim_count = 0
        cluster = 0
        features = get_features(item[1], item[2])
        sim = Simhash(features)
        nears = index.get_near_dups(sim)
        if len(nears) > 0:
            sim_count = len(nears)
            cursor.execute(
                'select cluster from entries where id = %s', (int(nears[0]), ))
            near_cluster = cursor.fetchone()[0]
            cluster = near_cluster
        else:
            cluster = cluster_num
            cluster_num += 1

        cursor.execute('UPDATE entries SET cluster=%s, sim_count=%s, simhash=%s where id = %s', (
            cluster, sim_count, str(sim.value), item[0]))

        index.add(str(item[0]), sim)

        # entrydic[str(item[0])] = {
        #     'cluster': 0,
        #     'sim_count': 0,
        #     'simhash': sim
        # }

    # cluster_num = 0
    # for key in entrydic:
    #     if entrydic[key]['cluster'] == 0:
    #         print(key)
    #         sims = index.get_near_dups(
    #             entrydic[key]['simhash'])
    #         for item in sims:
    #             entrydic[item]['cluster'] = cluster_num
    #             # if len(sims) > 1:
    #             entrydic[item]['sim_count'] = len(sims) - 1
    #             # if len(sims) > 1:
    #                 # fout.write(item + '\t' + str(entrydic[item]['cluster']) + '\t' + entrydic[item]['title'] + '\t' + entrydic[item]['link']  + '\n')
    #             cursor.execute('UPDATE entries SET cluster=%s, sim_count=%s, simhash=%s where id = %s', (entrydic[item]['cluster'], entrydic[item]['sim_count'], str(entrydic[item]['simhash'].value), item))
    #             # conn.commit()
    #             # fout.write(item + '\t' + str(entrydic[item]['cluster']) + '\t' + entrydic[item]['title'] + '\t' + entrydic[item]['link'] + '\n')
    #         cluster_num += 1
    # # cursor.execute('UPDATE somevariables SET last_cluster=%s', (cluster_num,))
    # # conn.commit()
    conn.close()


restore_simhash()
clustering()
