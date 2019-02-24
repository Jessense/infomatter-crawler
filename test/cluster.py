# coding=gbk
import jieba
from simhash import Simhash, SimhashIndex
import requests
import json
import ast
import time

tolerance = 10  # ���̶ȣ��ж��ǲ��������õ�

response = requests.get('http://188.131.178.76:3000/entries/cluster/100')
response_text = response.text
entryset = ast.literal_eval(response_text)

# ****************ͣ�ôʿ�
file = open('./stopwords.txt', 'r', encoding='UTF-8')
lines = file.readlines()

stopwords = set()
# print(lines)
for line in lines:
    word = ''
    for letter in line:
        if (letter != '\ufeff') and (letter != ' ') and (letter != '\n'):
            word += letter
    stopwords.add(word)
# print(stopwords)
# **************************************************


datadic = {}

# �ִ�,ȥͣ�ôʣ����������


def segmentation(entryset, stopwords):
    for entry in entryset:
        datadic[entry["id"]] = (" ".join(jieba.cut(entry["title"]))).split()  # �ִ�
        for wordlist in datadic.values():  # ȥͣ�ô�
            for word in wordlist:
                if word in stopwords:
                    wordlist.remove(word)




#print(datadic)


def simhashsort(datadic, entryset):
    objs = [(id, Simhash(sent)) for id, sent in datadic.items()]
    index = SimhashIndex(objs, k = tolerance)  # k�����̶ȣ�kԽ�󣬼������������ı���Խ��
    kind = 1  # ���ͺ�
    sorted = set()
    for id in datadic:
        if str(id) in sorted:  # ���ظ�����
            continue
        # �����Ƽ�
        similiarlist = index.get_near_dups(Simhash(datadic[id]))
        similiarlist.append(str(id))
        # �����Ƽ���Ϣ���ص�entryset��
        for id in similiarlist:
            sorted.add(id)
        for entry in entryset:
            if str(entry["id"]) in similiarlist:
                entry["cluster"] = kind
        kind += 1

# ����Ϊ����
start = time.clock()
segmentation(entryset, stopwords)
simhashsort(datadic, entryset)
print(time.clock()-start)
# print(entryset)


# result = {}
# for entry in entryset:
#     if entry["cluster"] not in result:
#         result[entry["cluster"]] = 0
#     result[entry["cluster"]] += 1
# #     #print(entry)
# #     if entry["cluster"] == 21:
# #         print(entry['title'])
# for key in result:
#     if result[key] >= 10:
#         print(str(key) + ' : ' + str(result[key]))
#         for entry in entryset:
#             if entry['cluster'] == key:
#                 print(str(entry['id']) +'\t'+ entry['title'])
