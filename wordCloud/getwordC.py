#!/usr/bin/python3  
# -*- coding: utf-8 -*-
# @Time    : 2021/3/25 12:42 PM
# @Author  : Zhihu Yang
# @File    : getwordC.py
import jieba
import pandas as pd
import wordcloud
import matplotlib.pyplot as plt
from imageio import imread

# 读取数据
file_name = '/Users/zhihuyang/IdeaProjects/ddmcData/dataset/result.csv'
df = pd.read_csv(file_name, encoding='utf-8', names=['content'])
backgroud_Image = imread('/Users/zhihuyang/IdeaProjects/ddmcData/wordCloud/img_1.png')
img_colors = wordcloud.ImageColorGenerator(backgroud_Image)

# 清洗数据
# 为了在处理数据时不会因为某条数据有问题，导致整个任务停止，故使用try except continue
df = df.dropna()
content = df["content"].values.tolist()
segment = []
for line in content:
    try:
        segs = jieba.lcut(line)
        for seg in segs:
            if len(seg) > 1 and seg != '\r\n\t':
                segment.append(seg)
    except:
        print(line)
        continue

# 去除停用词
words_df = pd.DataFrame({'segment': segment})
stopwords = pd.read_csv("/Users/zhihuyang/IdeaProjects/ddmcData/wordCloud/stopwords.txt", index_col=False, quoting=3,
                        sep='\t', names=['stopword'], encoding='utf-8')
words_df = words_df[~words_df.segment.isin(stopwords.stopword)]
words_stst = words_df.groupby('segment').agg(
    计数=pd.NamedAgg(column='segment', aggfunc='size')).reset_index().sort_values(
    by='计数', ascending=False)
words_stat = words_stst.reset_index().sort_values(by=['计数'], ascending=False)
word_frequence = {x[0]: x[1] for x in words_stat.head(500).values}
result_str = " ".join(word_frequence.values())

font = r'/Users/zhihuyang/IdeaProjects/ddmcData/wordCloud/simsun.ttc'
w = wordcloud.WordCloud(font_path=font, width=500, height=500, max_words=40, background_color='white', mask=backgroud_Image)

result_str += ' 自提 质量 态度 恶劣 真香 团长 便宜'
w.generate(result_str)
w.to_file('ddmcWordCloud.png')
