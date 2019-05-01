import re
from lxml.html.clean import Cleaner

cleaner = Cleaner(style=True, scripts=True, comments=True,
                  javascript=True, page_structure=False, safe_attrs_only=True)

content = '''
这是一只低像素喵。<br /><br />——Zannmuling <img referrerpolicy=\"no-referrer\" src=\"https://wx2.sinaimg.cn/large/7e948b4dly1g2g2248j8aj20k00qotaf.jpg\"><br><br><img referrerpolicy=\"no-referrer\" src=\"https://wx2.sinaimg.cn/large/7e948b4dly1g2g2248iykj20k00qoabt.jpg\"><br><br>
'''


# def getImg(html):
#     reg = r'(.*?|\n)<img [^\>|\n]*src\s*=\s*([\"\'])(.*?)\2'
#     matchObj = re.match(reg, content, re.DOTALL)
#     if matchObj:
#         return matchObj.group(3)    
#     else:
#         return ''

def filter_tags(htmlstr):
  re_cdata = re.compile(r'//<!\[CDATA\[[^>]*//\]\]>', re.I)  # 匹配CDATA
  re_script = re.compile(
      r'<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', re.I)  # Script
  re_style = re.compile(r'<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)  # style
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

def getWeiboImg(html):
    reg = r'(.*?|\n)<img [^\>|\n]*src\s*=\s*([\"\'])(.*?)\2'
    results = re.findall(reg, content, re.DOTALL)
    if len(results) > 0:
        imgs = '['
        for i in range(len(results)):
            imgs += "\"" + results[i][2] + "\""
            if i < len(results) - 1:
                imgs += ','
        imgs += ']'
        return imgs
    else:
        return ''


print(getWeiboImg(content))

