#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：python-note 
@File    ：app.py
@IDE     ：PyCharm 
@Author  ：wly
@Date    ：2025/9/25 15:27 
@Description: 
'''
from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_flask():
    return 'hello flask'

# v1.0之后的版本，不推荐的写法
# if __name__ == '__main__':
#     app.run()
