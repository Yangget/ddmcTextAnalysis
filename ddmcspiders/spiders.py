#!/usr/bin/python3  
# -*- coding: utf-8 -*-
# @Time    : 2021/3/24 5:40 PM
# @Author  : Zhihu Yang
# @File    : spiders.py

import requests
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt
from pylab import mpl
import csv

# 设置字体
mpl.rcParams['font.sans-serif'] = r'/Users/zhihuyang/IdeaProjects/super-calculator/tools/simsun.ttc'
mpl.rcParams['axes.unicode_minus'] = False


def getPageText(url):
    fina_res = []
    try:
        # 获取数据
        r = requests.get(url)
        r.raise_for_status()
        r.encoding = 'UTF-8'
        soup = BeautifulSoup(r.text, 'html.parser')
        data = soup.find_all('p')
        d_list = []
        for item in data:
            d_list.append(item.text)
        words = d_list[4:-11:]

        # 切出微博正文
        for index, f_r in enumerate(words):
            if f_r.find('多多买菜') > 0:
                fina_res.append([f_r.replace(" ", "").replace("\n", "").replace("\u200b", "")])
    except:
        pass
    return fina_res


def getAllData():
    # 所有的数据
    # All_data = []
    # 网址
    url = 'https://s.weibo.com/weibo?q=多多买菜&scope=ori&suball=1&Refer=g&page=1'
    # csv路径
    file_name = 'ddmcComment.csv'
    # 爬取每一页
    # for i in range(1, Pages):
    All_data = getPageText(url)

    try:
        # 读入数据
        f = open(file_name, 'r')
        csvreader = csv.reader(f)
        final_list = list(csvreader)

        # 取并集
        jijiao = []
        for A_d in final_list:
            if A_d not in All_data:
                jijiao.append(A_d)

        All_data.extend(jijiao)
    except:
        pass

    with open(file_name, 'w',encoding = 'utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for row in All_data:
            writer.writerow(row)


    # key = list(set(redata))
    # x, y = [], []
    # # 筛选数据
    # for st in key:
    #     count = redata.count(st)
    #     if count <= 1:
    #         continue
    #     else:
    #         x.append(st)
    #         y.append(count)
    # x.sort()
    # y.sort()
    #
    # # 绘制结果图
    # plt.plot(x, y)
    # plt.show()

if __name__ == '__main__':
    getAllData()
