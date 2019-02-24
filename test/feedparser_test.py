import feedparser
results = feedparser.parse("http://www.stats.gov.cn/tjsj/zxfb/rss.xml")
feed = results['feed']
items = results['items']
for key in feed:
    print(key + " : " + str(feed[key]))

for key in items[0]:
    print(key + " : " + str(items[0][key]))
