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

SENTENCES_COUNT = 5
TZ_DELTA = 8


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
    feedUrl = "https://news.ycombinator.com/rss"
    LANGUAGE = 'chinese'
    items = feedparser.parse(feedUrl)['items']
    for item in items:
        entry = {
            'title': item['title'],
            'link': item['link'],
            'source_id': '',
            'source_name': '',
            'time': '',
            'crawl_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'photo': '',
            'lang': '',
            'author': '',
            'description': '',
            'digest': '',
            'content': ''
        }
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

        parser = HtmlParser.from_string(
            entry['content'], "", Tokenizer(LANGUAGE))
        stemmer = Stemmer(LANGUAGE)
        summarizer = Summarizer(stemmer)
        summarizer.stop_words = get_stop_words(LANGUAGE)
        for sentence in summarizer(parser.document, SENTENCES_COUNT):
            entry['digest'] += str(sentence)
        print('title:'+entry['title'])
        print('photo:'+entry['photo'])
        print(item['comments'])
        # print('content:'+entry['content'])
crawl()
