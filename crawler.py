# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timedelta, timezone
from time import mktime
import time
import feedparser
import re
import mysql.connector
# 注意把password设为你的root口令:
conn = mysql.connector.connect(user='root', password='infomatter666', database='test')
SENTENCES_COUNT = 5
TZ_DELTA = 8

add_entry = ("INSERT INTO entries "
            "(title, link, source_id, source_name, time, crawl_time, photo, author, lang, description, digest, content) "
            "VALUES (%(title)s, %(link)s, %(source_id)s, %(source_name)s, %(time)s, %(crawl_time)s, %(photo)s, %(author)s, %(lang)s, %(description)s, %(digest)s, %(content)s)")

# stemmer_cn = Stemmer('chinese')
# summarizer_cn = Summarizer(stemmer)
# summarizer_cn.stop_words = get_stop_words('chinese')

# stemmer_en = Stemmer('english')
# summarizer_en = Summarizer(stemmer)
# summarizer_en.stop_words = get_stop_words('english')


def getImg(html):
    reg = r'(.*?|\n)<img [^\>|\n]*src\s*=\s*([\"\'])(.*?)\2'
    matchObj = re.match(reg, html, re.DOTALL)
    if matchObj:
        return matchObj.group(3)
    return ''

def crawl():
    print(datetime.now())
    cursor = conn.cursor()
    cursor.execute("SET NAMES utf8mb4")
    cursor.execute('select id, name, feedUrl, lang, form, content_rss from sources')
    sources = cursor.fetchall()
    start = time.clock()
    for source in sources:
        # if source['id']%30 == datetime.now().minute%30:
        print(source[0])
        source = {
            'id': source[0],
            'name': source[1],
            'feedUrl': source[2].replace("188.131.178.76", "127.0.0.1"),
            'lang': source[3],
            'form': source[4],
            'content_rss': source[5]
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
                        'lang': source['lang'],
                        'author': '',
                        'description': '',
                        'digest': '',
                        'content': ''
                    }
                    ############ Additonal Settings for special sources ##############
                    if entry['source_name'] == 'Hacker News':
                        entry['link'] = item['comments']
                    ###########################
                    if 'published_parsed' in item:
                        entry['time'] = datetime.fromtimestamp(mktime(item['published_parsed'])) + timedelta(hours=TZ_DELTA)
                    else:
                        entry['time'] = entry['crawl_time']
                    if 'author' in item:
                        entry['author'] = item['author'][0:20]
                    if 'content' in item:
                        entry['content'] = item['content'][0]['value']
                    if entry['content'] == '':
                        entry['content'] = item['summary']
                    if entry['content'] != '':
                        entry['photo'] = getImg(entry['content'])
                        if len(entry['photo']) > 255:
                            entry['photo'] = ''
                    if source['form'] == 1:
                        if source['content_rss'] == 1 and entry['content'] != '':
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
                    cursor.execute(add_entry, entry)
                    conn.commit()
                except Exception as e:
                    print("Unexpected Error: {}".format(e))

        # print(d['feed']['title'])
    elapsed = time.clock() - start
    print('time used: ' + str(elapsed))


    # 关闭Cursor和Connection:
    cursor.close()



sched = BlockingScheduler()
sched.add_job(crawl, 'interval', minutes=30)
sched.start()


conn.close()

