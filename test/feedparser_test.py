import feedparser
results = feedparser.parse("https://www.youtube.com/feeds/videos.xml?channel_id=UCoookXUzPciGrEZEXmh4Jjg")
feed = results['feed']
items = results['items']
for key in feed:
    print(key + " : " + str(feed[key]))

for field in items[0]['links']:
    if field['type'] == 'audio/mpeg':
        print(field['href'])

# for key in items[0]:
#     print(key + " : " + str(items[0][key]))
    
