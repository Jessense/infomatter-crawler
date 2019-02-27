# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from simhash import Simhash, SimhashIndex

import nltk
import jieba

from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timedelta, timezone
from time import mktime
import time
import feedparser
import re
import mysql.connector
from bs4 import BeautifulSoup
from aip import AipNlp

from config import *





client = AipNlp(APP_ID, API_KEY, SECRET_KEY)


# 注意把password设为你的root口令:
conn = mysql.connector.connect(user='root', password=sql_password, database='test')
conn.autocommit = True




add_entry = ("INSERT INTO entries "
            "(title, link, source_id, source_name, time, crawl_time, photo, lang, author, description, digest, content, cluster, sim_count, simhash, cate11, cate12, cate13, cate21, cate22, cate23, tag1, tag2, tag3, tag4, tag5) "
             "VALUES (%(title)s, %(link)s, %(source_id)s, %(source_name)s, %(time)s, %(crawl_time)s, %(photo)s, %(lang)s, %(author)s, %(description)s, %(digest)s, %(content)s, %(cluster)s, %(sim_count)s, %(simhash)s, %(cate11)s, %(cate12)s, %(cate13)s, %(cate21)s, %(cate22)s, %(cate23)s, %(tag1)s, %(tag2)s, %(tag3)s, %(tag4)s, %(tag5)s)")


last_cluster_num = 0

objs = []
index = SimhashIndex(objs, k=tolerance)
def restore_simhash():
    global last_cluster_num
    cursor = conn.cursor()
    cursor.execute('select id, simhash from entries where simhash > 0')
    entries = cursor.fetchall()
    for entry in entries:
        index.add(str(entry[0]), Simhash(int(entry[1])))

    cursor.execute('select max(cluster) from entries')
    last_cluster_num = cursor.fetchone()[0] + 1

def getImg(html):
    reg = r'(.*?|\n)<img [^\>|\n]*src\s*=\s*([\"\'])(.*?)\2'
    matchObj = re.match(reg, html, re.DOTALL)
    if matchObj:
        return matchObj.group(3)
    return ''


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
    if is_en(s):
        punc = list('`~!@#$%^&*()_+-={}|:\"<>?[]\\;\',./')
        s = s.lower()
        s = nltk.word_tokenize(s)
        for word in s:
            if word in get_stop_words('english') or word in punc:
                s.remove(word)
        return s
    else:
        punc = list('·~！!@#￥$%…&*（）()_——+-={}|、：:\'\"\\“”《》<>？?【】[]；‘’，。,./')
        s = s.lower()
        s = (" ".join(jieba.cut(s))).split()
        for word in s:
            if word in get_stop_words('chinese') or word in punc:
                s.remove(word)
        return s

def crawl():
    print(datetime.now())
    cursor = conn.cursor()
    cursor.execute("SET NAMES utf8mb4")
    cursor.execute('select id, name, feedUrl, lang from sources')
    sources = cursor.fetchall()
    start = time.clock()
    for source in sources:
        # if source['id']%30 == datetime.now().minute%30:
        print(source[0])
        source = {
            'id': source[0],
            'name': source[1],
            'feedUrl': source[2].replace("188.131.178.76", "127.0.0.1"),
            'lang': source[3]
        }
        print(source['name'])
        LANGUAGE = 'chinese'
        if source['lang'] == 2:
            LANGUAGE = 'english'
        items = feedparser.parse(source['feedUrl'])['items']
        for item in items:
            cursor.execute('select 1 from entries where link = %s and title = %s limit 1', (item['link'], item['title']))
            results = cursor.fetchall()
            if (not results) or (len(results) == 0):
                try:
                    entry = {
                        'title': item['title'],
                        'link': item['link'],
                        'source_id': source['id'],
                        'source_name': source['name'],
                        'time': '',
                        'crawl_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'photo': '',
                        'lang': 1,
                        'author': '',
                        'description': '',
                        'digest': '',
                        'content': '',
                        'cluster': 0,
                        'sim_count': 0,
                        'simhash': '0',
                        'cate11': '',
                        'cate12': '',
                        'cate13': '',
                        'cate21': '',
                        'cate22': '',
                        'cate23': '',
                        'tag1': '',
                        'tag2': '',
                        'tag3': '',
                        'tag4': '',
                        'tag5': ''
                    }
                    ############ Additonal Settings for special sources ##############
                    if entry['source_name'] == 'Hacker News':
                        entry['link'] = item['comments']
                    ###########################

                    if is_en(entry['title']):
                        entry['lang'] = 2
                    if 'summary' in item:
                        entry['description'] = item['summary'][0:500]
                    if 'published_parsed' in item:
                        entry['time'] = datetime.fromtimestamp(mktime(item['published_parsed'])) + timedelta(hours=TZ_DELTA)
                    else:
                        entry['time'] = entry['crawl_time']

                    if 'author' in item:
                        entry['author'] = item['author'][0:20]

                    if 'content' in item:
                        entry['content'] = item['content'][0]['value'][0:15000]
                    if entry['content'] == '' and 'summary' in item and len(item['summary']) > 0:
                        entry['content'] = item['summary'][0:15000]

                    try:
                        if entry['content'] != '':
                            entry['photo'] = getImg(entry['content'])
                            if len(entry['photo']) > 255:
                                entry['photo'] = ''

                            parser = HtmlParser.from_string(entry['content'], "", Tokenizer(LANGUAGE))
                            stemmer = Stemmer(LANGUAGE)
                            summarizer = Summarizer(stemmer)
                            summarizer.stop_words = get_stop_words(LANGUAGE)
                            for sentence in summarizer(parser.document, SENTENCES_COUNT):
                                entry['digest'] += str(sentence)
                                if len(entry['digest']) >= 500:
                                    break
                        else:
                            parser = HtmlParser.from_url(entry['link'], Tokenizer(LANGUAGE))
                            stemmer = Stemmer(LANGUAGE)
                            summarizer = Summarizer(stemmer)
                            summarizer.stop_words = get_stop_words(LANGUAGE)
                            for sentence in summarizer(parser.document, SENTENCES_COUNT):
                                entry['digest'] += str(sentence)
                                if len(entry['digest']) >= 500:
                                    break
                        entry['digest'] = entry['digest'][0:500]
                    except Exception as e:
                        print('Exception when getting digest: {}'.format(e))

                    try:
                        if len(entry['title']) > 0 and len(get_features(entry['title'])) >= 2:
                            entry['simhash'] = str(Simhash(get_features(entry['title'])).value)
                            nears = index.get_near_dups(Simhash(get_features(entry['title'])))
                            if len(nears) > 0:
                                entry['sim_count'] = len(nears)
                                cursor.execute('select cluster from entries where id = %s', (int(nears[0]), ))
                                near_cluster = cursor.fetchone()[0]
                                entry['cluster'] = near_cluster
                            else:
                                global last_cluster_num
                                entry['cluster'] = last_cluster_num
                                last_cluster_num += 1
                    except Exception as e:
                        print('Exception when clustering: {}'.format(e))

                    cate1 = ['', '', '']
                    cate2 = ['', '', '']
                    tag = ['', '', '', '', '']
                    try:
                        content2 = BeautifulSoup(entry['content'], "lxml").text.encode(
                            'gbk', 'ignore').decode('gbk')[0:AIP_MAX_LEN_CONTENT]
                        if len(content2) == 0:
                            if len(entry['digest']) > 0:
                                content2 = entry['digest']
                        title2 = entry['title'][0:AIP_MAX_LEN_TITLE]
                        keywords = client.keyword(title2, content2)
                        topics = client.topic(title2, content2)
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
                        entry['cate11'] = cate1[0]
                        entry['cate12'] = cate1[1]
                        entry['cate13'] = cate1[2]
                        entry['cate21'] = cate2[0]
                        entry['cate22'] = cate2[1]
                        entry['cate23'] = cate2[2]
                        entry['tag1'] = tag[0]
                        entry['tag2'] = tag[1]
                        entry['tag3'] = tag[2]
                        entry['tag4'] = tag[3]
                        entry['tag5'] = tag[4]
                    except Exception as e:
                        print('Exception when categorizing and tagging: {}'.format(e))


                    try:
                        cursor.execute(add_entry, entry)
                        index.add(str(cursor.lastrowid), Simhash(get_features(entry['title'])))
                    except Exception as e:
                        print('Exception when add entry: {}'.format(e))
                except Exception as e:
                    print("Unexpected Error: {}".format(e))

        # print(d['feed']['title'])
    elapsed = time.clock() - start
    print('time used: ' + str(elapsed))


    # 关闭Cursor和Connection:
    cursor.close()


# restore_simhash()
# sched = BlockingScheduler()
# sched.add_job(crawl, 'interval', minutes=30)
# sched.start()

restore_simhash()
crawl()

conn.close()

