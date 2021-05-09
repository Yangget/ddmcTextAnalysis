#!/usr/bin/python3  
# -*- coding: utf-8 -*-
# @Time    : 2021/3/25 2:52 PM
# @Author  : Zhihu Yang
# @File    : testddmc.py
import warnings

warnings.filterwarnings("ignore")

import csv
from Sentiment_lstm import lstm_predict


# 读取数据
def getAllDate(file_name):
    f = open(file_name, 'r')
    csvreader = csv.reader(f)
    return list(csvreader)


# 得到数据的情感倾向
def getSent(data):
    result = []
    for d in data:
        string, label = lstm_predict("".join(d))
        result.append([string, label])
    return result


def writeData(result, file_name):
    with open(file_name, 'w', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for row in result:
            writer.writerow(row)


if __name__ == '__main__':
    data = getAllDate(file_name='/Users/zhihuyang/IdeaProjects/ddmcData/dataset/result.csv')

    result = getSent(data)

    writeData(file_name='ddmcSentAnalysis.csv', result=result)
