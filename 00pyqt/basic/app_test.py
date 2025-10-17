#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：python-note 
@File    ：app_test.py
@IDE     ：PyCharm 
@Author  ：wei liyu
@Date    ：2025/10/16 10:27 
'''
import sys
from PyQt5.QtWidgets import QApplication, QWidget

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = QWidget()
    w.resize(400, 200)
    w.move(300, 300)
    w.setWindowTitle('第一个窗口')
    w.show()
    sys.exit(app.exec_())
