#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：python-note 
@File    ：app.py
@IDE     ：PyCharm 
@Author  ：wei liyu
@Date    ：2025/10/17 20:05 
'''
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow

from TagLib.taglib import Ui_MainWindow


def main():
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(mainWindow)
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
