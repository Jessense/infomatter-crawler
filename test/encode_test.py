# -*- coding: utf-8 -*-
a = '\xa0'
print(a)

b = '女'
print('a == b? ', a == b)

s1 = b.encode('gbk').decode('gbk')
print('s1:', s1)
s2 = a.encode('gbk').decode('gbk')
print('s2', s2)
