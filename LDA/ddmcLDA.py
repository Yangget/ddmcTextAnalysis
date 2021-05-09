#!/usr/bin/python3  
# -*- coding: utf-8 -*-
# @Time    : 2021/3/25 3:26 PM
# @Author  : Zhihu Yang
# @File    : ddmcLDA.py

from gensim import corpora, models
import jieba.posseg as jp
import jieba
import csv

# 参数
file_name = '/Users/zhihuyang/IdeaProjects/ddmcData/dataset/result.csv'

# 文本集
f = open(file_name, 'r')
csvreader = csv.reader(f)
texts = list(csvreader)


# 创建停用词表
def stopwordslist(filepath='/Users/zhihuyang/IdeaProjects/ddmcData/wordCloud/stopwords.txt'):
    stopwords = [line.strip() for line in open(filepath, 'r', encoding='utf-8').readlines()]
    return stopwords


# 分词过滤条件
jieba.load_userdict('mydict.txt')
jieba.suggest_freq(('多多买菜', '拼多多', '美团'), True)  # 动态调整词频，使其能/不能被分出来
flags = ('n', 'nr', 'ns', 'nt', 'eng', 'v', 'd')  # 词性
stopwords = stopwordslist()

# 分词
words_ls = []
for text in texts:
    words = [word.word for word in jp.cut(("".join(text)).replace(" ",""), HMM=False)
             if word.flag in flags
             # word.word not in stopwords
    ]
    words_ls.append(words)

# 构造词典
dictionary = corpora.Dictionary(words_ls)
# 基于词典，使【词】→【稀疏向量】，并将向量放入列表，形成【稀疏向量集】
corpus = [dictionary.doc2bow(words) for words in words_ls]
# lda模型，num_topics设置主题的个数
lda = models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary, num_topics=2)

# 打印所有主题，每个主题显示4个词
for topic in lda.print_topics(num_words=8):
    print(topic)

# 主题推断
# for e, values in enumerate(lda.inference(corpus)[0]):
#     print(texts[e])
#     for ee, value in enumerate(values):
#         print('\t主题%d推断值%.2f' % (ee, value))
