import html2text
import requests
import ast
from jieba.analyse import *
from my_tfidf import *
from simhash import Simhash, SimhashIndex

response = requests.get('http://api.infomatter.cn/entries/1000')
data = ast.literal_eval(response.text)


# print(type(data))
# 先把content中的好宝贝搞出来


def preprocess(data_list):
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_images = True
    h.ignore_emphasis = True
    for entry in data_list:
        content = h.handle(entry["content"])
        content = content.replace(" ", "")
        content = content.replace(" ", "")
        entry["content"] = content.replace("\n", "")


# 然后提取关键词，哈哈
# 策略是这样的，内容和标题各自求tag,标题占比大一些，然后阈值过滤一下，取weight最大的几个 （不是这样的，没按这个搞）
# 策略是这样的，标题内容先连起来搞tmd

def extract(data_list):
    # title_ratio_content，标题权重与内容权重之比
    trc = 0.1
    trc_coe = 1.2   # trc系数

    # 添加去停用词
#     set_stop_words('stop_words.txt')
    my_tfidf = TFIDF()
    for entry in data_list:  # 对每一条entry
        tag_dict = dict()
        # 计算trc
        # trc = trc_coe*len(entry["title"])/len(entry["content"])
        # 对标题求tag
    #    for tag, weight in extract_tags(entry["title"], topK=5, withWeight=True):
    #        if weight > 0.1:
    #            tag_dict[tag] = weight * trc  # 加权
        # 对内容
        for tag, weight in extract_tags(entry["title"]+entry["content"], topK=20, withWeight=True):
            # for tag, weight in my_tdidf.extract_tags(entry["title"] + entry["content"], topK=20, withWeight=True):
            if weight > 0.1:  # 设定一个阈值
                tag_dict[tag] = weight
        tag_list = sorted(tag_dict.items(), key=lambda x: x[1], reverse=True)
    #   for i in range(len(sorted(tag_dict.items(), key=lambda x: x[1], reverse=True))):

        entry["tags"] = tag_list


def simhashSort2(datadic, entryset):
    objs = []
    for entry in datadic:
        objs.append((entry[0], Simhash(entry[1])))
    index = SimhashIndex(objs, k=tolerance)  # k是容忍度；k越大，检索出的相似文本就越多
    kind = 1  # 类型号
    sorted = set()
    for item in datadic:
        if str(item[0]) in sorted:  # 不重复分类
            continue
        # 求相似集
        similiarlist = index.get_near_dups(Simhash(item[1]))
        similiarlist.append(str(item[1]))
        # 将相似集信息返回到entryset中
        for id in similiarlist:
            sorted.add(id)
        for entry in entryset:
            if str(entry["id"]) in similiarlist:
                entry["sim_count"] = kind
        kind += 1

# main


if __name__ == "__main__":
    # [('技术', 8.000152594346165), ('采用', 6.164310067098711), ('区块', 5.875865292966604), ('企业', 3
    tolerance = 7
    # [('技术', 9.585975139350845), ('红包', 3.7829889442097677), ('百度', 3.3626568392975713), ('春晚',
    preprocess(data)
    extract(data)
    result_list = []  # 许多条 id 和 tag
   #  result_tags = []  # id 和 tag

    for entry in data:
        result_tags = []
        result_tags.append(entry["id"])
        result_tags.append(entry["tags"])
        result_list.append(result_tags)
        print(entry["id"], entry["tags"])

    print(result_list)

    simhashSort2(result_list, data)
    for entry in data:
        print(entry["id"], entry["sim_count"])

    showed = []
    for entry in data:
        if entry["sim_count"] not in showed:
            for item in data:
                if item["sim_count"] == entry["sim_count"]:
                    print(item["id"], item["sim_count"], item["tags"])
        else:
            showed.append(entry["sim_count"])
