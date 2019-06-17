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
import jieba.analyse

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
conn = mysql.connector.connect(
    user='root', password=sql_password, database='test')
conn.autocommit = True


add_entry = ("INSERT IGNORE INTO entries "
             "(title, link, source_id, source_name, time, crawl_time, photo, lang, author, description, digest, content, cluster, sim_count, simhash, cate11, cate12, cate13, cate21, cate22, cate23, tag1, tag2, tag3, tag4, tag5, video, video_frame, audio, audio_frame) "
             "VALUES (%(title)s, %(link)s, %(source_id)s, %(source_name)s, %(time)s, %(crawl_time)s, %(photo)s, %(lang)s, %(author)s, %(description)s, %(digest)s, %(content)s, %(cluster)s, %(sim_count)s, %(simhash)s, %(cate11)s, %(cate12)s, %(cate13)s, %(cate21)s, %(cate22)s, %(cate23)s, %(tag1)s, %(tag2)s, %(tag3)s, %(tag4)s, %(tag5)s, %(video)s, %(video_frame)s, %(audio)s, %(audio_frame)s)")


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


def getWeiboImg(html):
    reg = r'(.*?|\n)<img [^\>|\n]*src\s*=\s*([\"\'])(.*?)\2'
    results = re.findall(reg, html, re.DOTALL)
    if len(results) > 0:
        imgs = '['
        for i in range(len(results)):
            imgs += "\"" + results[i][2] + "\""
            if i < len(results) - 1:
                imgs += ','
        imgs += ']'
        return imgs
    else:
        return '[]'


def filterWeiboTags(htmlstr):
    re_cdata = re.compile(r'//<!\[CDATA\[[^>]*//\]\]>', re.I)  # 匹配CDATA
    re_script = re.compile(
        r'<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', re.I)  # Script
    re_style = re.compile(
        r'<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)  # style
    re_br = re.compile(r'<br\s*?/?>')  # 处理换行
    re_h = re.compile(r'</?\w+[^>]*>')  # HTML标签
    re_comment = re.compile(r'<!--[^>]*-->')  # HTML注释
    blank_line = re.compile(r'\n+')

    #过滤匹配内容
    s = re_cdata.sub('', htmlstr)  # 去掉CDATA
    s = re_script.sub('', s)  # 去掉SCRIPT
    s = re_style.sub('', s)  # 去掉style
    s = re_br.sub('\n', s)  # 将br转换为换行
    s = re_h.sub('', s)  # 去掉HTML 标签
    s = re_comment.sub('', s)  # 去掉HTML注释
    s = blank_line.sub('\n', s)  # 去掉多余的空行

    return s


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

# def get_features(s):
#     if is_en(s):
#         punc = list('`~!@#$%^&*()_+-={}|:\"<>?[]\\;\',./')
#         s = s.lower()
#         s = nltk.word_tokenize(s)
#         for word in s:
#             if word in get_stop_words('english') or word in punc:
#                 s.remove(word)
#         return s
#     else:
#         punc = list('·~！!@#￥$%…&*（）()_——+-={}|、：:\'\"\\“”《》<>？?【】[]；‘’，。,./')
#         s = s.lower()
#         s = (" ".join(jieba.cut(s))).split()
#         for word in s:
#             if word in get_stop_words('chinese') or word in punc:
#                 s.remove(word)
#         return s


def crawl():
    print(datetime.now())
    cursor = conn.cursor()
    cursor.execute("SET NAMES utf8mb4")
    cursor.execute('select id, name, feedUrl, lang, form from sources')
    sources = cursor.fetchall()
    start = time.clock()
    for source in sources:
        # if source['id']%30 == datetime.now().minute%30:
        print(source[0])
        source = {
            'id': source[0],
            'name': source[1],
            'feedUrl': source[2].replace("39.105.127.55", "127.0.0.1"),
            'lang': source[3],
            'form': source[4]
        }
        print(source['name'])
        LANGUAGE = 'chinese'
        if source['lang'] == 2:
            LANGUAGE = 'english'
        items = feedparser.parse(source['feedUrl'])['items']
        for item in items:
            try:
                cursor.execute(
                    'select 1 from entries where link = %s limit 1', (item['link'], ))
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
                            'tag5': '',
                            'video': '',
                            'video_frame': '',
                            'audio': '',
                            'audio_frame': ''
                        }
                        cate1 = ['', '', '']
                        cate2 = ['', '', '']
                        tag = ['', '', '', '', '']
                        ############ Additonal Settings for special sources ##############
                        if entry['source_name'] == 'Hacker News':
                            entry['link'] = item['comments']
                        ###########################

                        if is_en(entry['title']):
                            entry['lang'] = 2
                        if 'published_parsed' in item:
                            try:
                                entry['time'] = datetime.fromtimestamp(
                                    mktime(item['published_parsed'])) + timedelta(hours=TZ_DELTA)
                            except Exception as e:
                                entry['time'] = entry['crawl_time']
                                print(
                                    'Exception when published_parsed: {}'.format(e))
                        else:
                            entry['time'] = entry['crawl_time']

                        if 'author' in item:
                            entry['author'] = item['author'][0:20]

                        if 'summary' in item:
                            entry['description'] = item['summary'][0:500]

                        if 'content' in item:
                            entry['content'] = item['content'][0]['value'][0:15000]
                        if entry['content'] == '' and 'summary' in item and len(item['summary']) > 0:
                            entry['content'] = item['summary'][0:15000]
                        for field in item['links']:
                            if field['type'] == 'audio/mpeg':
                                if field['href'].endswith('.mp3'):
                                    entry['audio'] = field['href']
                                if field['href'].endswith('.mp4'):
                                    entry['video'] = field['href']

                        #对于文章类entry才进行摘要、聚类、分类、标签
                        if source['form'] == 1:
                            try:
                                if entry['content'] != '':
                                    entry['photo'] = getImg(entry['content'])
                                    if len(entry['photo']) > 255:
                                        entry['photo'] = ''

                                    parser = HtmlParser.from_string(
                                        entry['content'], "", Tokenizer(LANGUAGE))
                                    stemmer = Stemmer(LANGUAGE)
                                    summarizer = Summarizer(stemmer)
                                    summarizer.stop_words = get_stop_words(
                                        LANGUAGE)
                                    for sentence in summarizer(parser.document, SENTENCES_COUNT):
                                        entry['digest'] += str(sentence)
                                        if len(entry['digest']) >= 500:
                                            break
                                else:
                                    parser = HtmlParser.from_url(
                                        entry['link'], Tokenizer(LANGUAGE))
                                    stemmer = Stemmer(LANGUAGE)
                                    summarizer = Summarizer(stemmer)
                                    summarizer.stop_words = get_stop_words(
                                        LANGUAGE)
                                    for sentence in summarizer(parser.document, SENTENCES_COUNT):
                                        entry['digest'] += str(sentence)
                                        if len(entry['digest']) >= 500:
                                            break
                                entry['digest'] = entry['digest'][0:500]
                            except Exception as e:
                                print('Exception when getting digest: {}'.format(e))

                            features = get_features(
                                entry['title'], entry['content'])
                            try:
                                entry['simhash'] = str(
                                    Simhash(features).value)
                                nears = index.get_near_dups(
                                    Simhash(features))
                                if len(nears) > 0:
                                    entry['sim_count'] = len(nears)
                                    cursor.execute(
                                        'select cluster from entries where id = %s', (int(nears[0]), ))
                                    near_cluster = cursor.fetchone()[0]
                                    entry['cluster'] = near_cluster
                                else:
                                    global last_cluster_num
                                    entry['cluster'] = last_cluster_num
                                    last_cluster_num += 1
                            except Exception as e:
                                print('Exception when clustering: {}'.format(e))

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
                                print(
                                    'Exception when categorizing and tagging: {}'.format(e))

                        elif source['form'] == 2:
                            entry['photo'] = getWeiboImg(entry['content'])
                            entry['digest'] = filterWeiboTags(entry['content'])
                            if len(entry['digest']) > 500:
                                entry['digest'] = entry['digest'][0:500]

                        elif source['form'] == 4:
                            if entry['link'].startswith('https://www.bilibili.com/video'):
                                entry['video_frame'] = 'http://player.bilibili.com/player.html?aid=' + \
                                    entry['link'][33:]

                        try:
                            cursor.execute(add_entry, entry)
                            conn.commit()
                            index.add(str(cursor.lastrowid), Simhash(features))
                        except Exception as e:
                            print('Exception when add entry: {}'.format(e))
                    except Exception as e:
                        print("Unexpected Error: {}".format(e))
            except Exception as e:
                print("Unexpected Error: {}".format(e))
        # print(d['feed']['title'])
    elapsed = time.clock() - start
    print('time used: ' + str(elapsed))

    # 关闭Cursor和Connection:
    cursor.close()


restore_simhash()
sched = BlockingScheduler()
sched.add_job(crawl, 'interval', minutes=30, max_instances=5)
sched.start()

# restore_simhash()
# crawl()

conn.close()

