#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：python-note 
@File    ：02线程.py
@IDE     ：PyCharm 
@Author  ：wly
@Date    ：2025/10/30 16:53 
@Description: 
'''
import time
from threading import Thread


def download_img(url):
    time.sleep(1)
    print(f'{url} 下载完成')


if __name__ == '__main__':
    start_time = time.time()
    t1 = Thread(target=download_img, args=('https://www.baidu.com/img/p1.png',))
    t2 = Thread(target=download_img, args=('https://www.baidu.com/img/p2.png',))
    t3 = Thread(target=download_img, args=('https://www.baidu.com/img/p3.png',))

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

    end_time = time.time()
    print(f'总耗时：{end_time - start_time}')
