import re
content = "<img src=\"https://alioss.gcores.com/uploads/article/4d97242a-e3c0-4ae3-9a87-707e65a45bba.png\" alt=\"\" />\n  <br>\n\n    <p><em>导语：昨天下午机核有幸受邀参加了《阿丽塔：战斗天使》的中国新闻发布会，主演罗莎&middot;萨拉查、克里斯托弗&middot;沃尔兹、制片人乔&middot;兰道、&ldquo;卡神&rdquo;詹姆斯&middot;卡梅隆、《铳梦》原作者木城雪户以及导演罗伯特&middot;罗德里格兹莅临现场。在发布会前，詹姆斯&middot;卡梅隆先生更合刘慈欣老师&ldquo;聊了聊&rdquo;他们对科幻小说与电影的理解。</em></p>\n\n    <div style=\"margin:20px 0;\">\n      <img style=\"max-width:100%;\" src=\"https://alioss.gcores.com/uploads/image/d68967fb-8894-437d-afab-8e04d2b5a4fe_watermark.jpg\" alt=\"\" />\n    </div>\n    <p style=\"margin-left:0cm; margin-right:0cm; text-align:justify\">"


def getImg(html):
    reg1 = r'src="(.*?\.jpg)" alt'
    reg2 = r'src="(.*?\.jpeg)" alt'
    reg3 = r'src="(.*?\.png)" alt'
    reg4 = r'src="(.*?\.webp)" alt'
    reg5 = r'src="(.*?\.gif)" alt'


    pattern = re.compile("|".join([reg1, reg2, reg3, reg4, reg5]))
    imglist = re.findall(pattern, content)
    
    if len(imglist) > 0:
        for item in imglist[0]:
            if len(item) > 0:
                return item
    return ""

print(getImg(content))
