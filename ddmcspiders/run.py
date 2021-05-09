#!/usr/bin/python3  
# -*- coding: utf-8 -*-
# @Time    : 2021/3/24 8:51 PM
# @Author  : Zhihu Yang
# @File    : run.py
import time
from spiders import getAllData


def re_exe(inc = 300):
    while True:
        getAllData()
        time.sleep(inc)

if __name__ == '__main__':
    re_exe()