#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：python-note 
@File    ：03线程池.py
@IDE     ：PyCharm 
@Author  ：wly
@Date    ：2025/10/30 17:02 
@Description: 
'''
from time import time, sleep
from concurrent import futures


def download_img(url):
    sleep(1)
    return f'{url} 下载完成'


if __name__ == '__main__':
    start_time = time()

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(download_img, range(20))
        print(results)
        for result in results:
            print(result)

    end_time = time()
    print(f'总耗时：{end_time - start_time}')
