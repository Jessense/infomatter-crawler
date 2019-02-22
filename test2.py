import re
content = '''
<img src="http://inews.gtimg.com/newsapp_bt/0/7810535826/641" style="display:block;"/>
<p class="text" style="TEXT-INDENT:2em">腾讯科技讯  日前，WCG-official官方微博宣布，《王者荣耀》正式列入WCG2019西安赛事的游戏项目，它也成为WCG首
个中国自研手游正式比赛项目。</p><p class="text" style="TEXT-INDENT:2em">《王者荣耀》所有玩家都可以通过网上报名的方式参与WCG预选赛，在比赛中崭露头角表现优
秀，即有机会作为国家代表出战WCG决赛。</p><p class="text" style="TEXT-INDENT:2em"><p align="center"></p></p>
'''


def getImg(html):
    reg = r'(.*?|\n)<img [^\>|\n]*src\s*=\s*([\"\'])(.*?)\2'
    matchObj = re.match(reg, content, re.DOTALL)
    if matchObj:
        return matchObj.group(3)    
    else:
        return ''

print(getImg(content))

