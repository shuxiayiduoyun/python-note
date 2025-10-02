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
    return 'hello flask. success!'


app.add_url_rule('/home', 'home', hello_flask)
print(app.url_map)


@app.route('/user')
@app.route('/user/<page>')
def list_user(page=100):
    return f'您好，你是第{page}页用户。'

# v1.0之后的版本，不推荐的写法
# if __name__ == '__main__':
#     app.run()

