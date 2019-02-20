import feedparser
import time
from time import mktime
from datetime import datetime, timedelta, timezone
TZ_HERE = timezone(timedelta(hours=8))
TZ_DELTA = 8

timetup = time.gmtime()
d = feedparser.parse('https://www.pingwest.com/feed')
items = d['items']
# dt = datetime.fromtimestamp(mktime(items[0]['published_parsed'])) + timedelta(hours=TZ_DELTA)
# print(dt)
# print(items[0]['published_parsed'])
# print(dt(*timetup[:6]).isoformat())
# print(items[0]['published_parsed'].strftime('%Y-%m-%d %H:%M:%S'))
for key in d['feed']:
    print(d['feed'][key])
# print(d['feed'])
for key in items[0]:
    print(key + ' : ' + str(items[0][key]))
