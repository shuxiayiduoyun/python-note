#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：python-note 
@File    ：01定义路由.py
@IDE     ：PyCharm 
@Author  ：wly
@Date    ：2025/11/1 10:54 
@Description: 
'''
from flask import Flask, request, render_template_string, make_response

app = Flask(__name__)


# 定义一个简单的 HTML 表单
form_html = '''
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Submit Form</title>
</head>
<body>
    <h1>Submit Your Username</h1>
    <form action="/submit" method="post">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username">
        <button type="submit">Submit</button>
    </form>
</body>
</html>
'''


@app.route('/')
def home():
    # return 'Welcome to the Home Page! Flask 哈喽！'
    # 显示表单
    return render_template_string(form_html)


@app.route('/about')
def about():
    return 'This is the About Page.'


@app.route('/greet/<name>')
def greet(name):
    return f'Hello, {name}!'


@app.route('/submit', methods=['POST'])
def submit():
    username = request.form.get('username')
    return f'Hello, {username}!'


@app.route('/custom_response')
def custom_response():
    response = make_response('This is a custom response!')
    response.headers['X-Custom-Header'] = 'Value'
    return response


if __name__ == '__main__':
    app.run(debug=True)
