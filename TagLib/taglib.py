#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：python-note 
@File    ：taglib.py
@IDE     ：PyCharm 
@Author  ：wei liyu
@Date    ：2025/10/17 20:28 
'''
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QObject
from PyQt5.QtGui import QTextOption, QColor
from PyQt5.QtWidgets import QTextBrowser, QVBoxLayout, QWidget, QTextEdit


class Ui_MainWindow(QObject):
    """
    主窗口UI类
    负责创建和管理主窗口的所有UI组件
    """

    def __init__(self):
        super().__init__()

    def setupUi(self, MainWindow):
        """
        初始化主窗口UI组件

        Args:
            MainWindow: 主窗口对象
        """
        # 设置主窗口基本属性
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1336, 820)
        MainWindow.setMinimumSize(QtCore.QSize(1200, 700))

        # 设置字体和光标
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(11)
        MainWindow.setFont(font)
        MainWindow.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        # 设置窗口图标
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("pics/logo.ico"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        MainWindow.setWindowIcon(icon)

        # 创建中央部件
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)

        # 设置主水平布局
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")

        # 创建左侧部件
        self._create_left_panel()

        # 添加分隔线
        self._create_vertical_separator()

        # 创建中央部件
        self._create_center_panel()

        # 添加分隔线
        self._create_vertical_separator_2()

        # 创建右侧部件
        self._create_right_panel()

        # 创建菜单栏
        self._create_menu_bar(MainWindow)

        # 创建状态栏
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        # 创建工具栏
        self._create_toolbar(MainWindow)

        # 重新翻译UI文本
        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def _create_left_panel(self):
        """创建左侧面板"""
        self.leftWidget = QtWidgets.QWidget(self.centralwidget)
        self.leftWidget.setMinimumSize(QtCore.QSize(300, 0))
        self.leftWidget.setMaximumSize(QtCore.QSize(300, 16777215))
        self.leftWidget.setObjectName("leftWidget")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.leftWidget)
        self.verticalLayout.setObjectName("verticalLayout")

        # 分组框1
        self.groupBox = QtWidgets.QGroupBox(self.leftWidget)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout.addWidget(self.groupBox)

        # 分组框2
        self.groupBox_2 = QtWidgets.QGroupBox(self.leftWidget)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout.addWidget(self.groupBox_2)

        self.horizontalLayout.addWidget(self.leftWidget)

    def _create_vertical_separator(self):
        """创建左侧垂直分隔线"""
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.horizontalLayout.addWidget(self.line_2)

    def _create_center_panel(self):
        """创建中央面板"""
        self.centerWidget = QtWidgets.QWidget(self.centralwidget)
        self.centerWidget.setObjectName("centerWidget")

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.centerWidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        # 表格视图
        self.tableView = QtWidgets.QTableView(self.centerWidget)
        self.tableView.setObjectName("tableView")
        self.horizontalLayout_2.addWidget(self.tableView)

        self.horizontalLayout.addWidget(self.centerWidget)

    def _create_vertical_separator_2(self):
        """创建右侧垂直分隔线"""
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout.addWidget(self.line)

    def _create_right_panel(self):
        """创建右侧面板"""
        self.rightWidget = QtWidgets.QWidget(self.centralwidget)
        self.rightWidget.setMinimumSize(QtCore.QSize(300, 0))
        self.rightWidget.setMaximumSize(QtCore.QSize(300, 16777215))
        self.rightWidget.setObjectName("rightWidget")

        self.gridLayout = QtWidgets.QGridLayout(self.rightWidget)
        self.gridLayout.setObjectName("gridLayout")

        # 创建标签页控件
        self._create_tab_widget()

        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.horizontalLayout.addWidget(self.rightWidget)

    def _create_tab_widget(self):
        """创建标签页控件"""
        self.tabWidget = QtWidgets.QTabWidget(self.rightWidget)
        self.tabWidget.setEnabled(True)
        self.tabWidget.setToolTip("")
        self.tabWidget.setObjectName("tabWidget")

        # 创建信息标签页
        self._create_info_tab()

        # 创建第二个标签页
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")

        self.tabWidget.addTab(self.tab_info, "")
        self.tabWidget.addTab(self.tab_2, "")

    def _create_info_tab(self):
        """创建信息标签页"""
        self.tab_info = QtWidgets.QWidget()
        self.tab_info.setObjectName("tab_info")

        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tab_info)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        # 标题行
        self._create_title_row()

        # 中文标题行
        self._create_chinese_title_row()

        # 年份行
        self._create_year_row()

        # 类型行
        self._create_type_row()

        # 期刊/会议行
        self._create_publication_row()

        # 中科院分区行
        self._create_zky_row()

        # CCF分区行
        self._create_ccf_row()

        # JCR分区行
        self._create_jcr_row()

        # IF影响因子行
        self._create_if_row()

        # DOI行
        self._create_doi_row()

        # URL行
        self._create_url_row()

        # 摘要部分
        self._create_abstract_section()

        # 保存按钮
        self._create_save_button()

    def _create_title_row(self):
        """创建标题输入行"""
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")

        self.label = QtWidgets.QLabel(self.tab_info)
        self.label.setMinimumSize(QtCore.QSize(64, 0))
        self.label.setMaximumSize(QtCore.QSize(64, 16777215))
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)

        # self.text_title = QtWidgets.QLineEdit(self.tab_info)
        self.text_title = QtWidgets.QTextEdit(self.tab_info)
        self.text_title.setObjectName("line_title")
        self.text_title.setPlaceholderText("输入文献标题...")
        self.text_title.setMaximumHeight(70)
        self.text_title.textChanged.connect(lambda: self.adjust_text_height(self.text_title))

        self.horizontalLayout_3.addWidget(self.text_title)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

    def _create_chinese_title_row(self):
        """创建中文标题输入行"""
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")

        self.label_12 = QtWidgets.QLabel(self.tab_info)
        self.label_12.setMinimumSize(QtCore.QSize(64, 0))
        self.label_12.setMaximumSize(QtCore.QSize(64, 16777215))
        self.label_12.setObjectName("label_12")
        self.horizontalLayout_13.addWidget(self.label_12)

        # self.line_title_2 = QtWidgets.QLineEdit(self.tab_info)
        self.line_title_2 = QtWidgets.QTextEdit(self.tab_info)
        self.line_title_2.setObjectName("line_title_2")
        self.line_title_2.setPlaceholderText("输入中文标题...")
        self.horizontalLayout_13.addWidget(self.line_title_2)
        self.line_title_2.setMaximumHeight(70)
        self.line_title_2.textChanged.connect(lambda: self.adjust_text_height(self.line_title_2))

        self.verticalLayout_2.addLayout(self.horizontalLayout_13)

    def _create_year_row(self):
        """创建年份输入行"""
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")

        self.label_3 = QtWidgets.QLabel(self.tab_info)
        self.label_3.setMinimumSize(QtCore.QSize(64, 0))
        self.label_3.setMaximumSize(QtCore.QSize(64, 16777215))
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_4.addWidget(self.label_3)

        self.line_year = QtWidgets.QLineEdit(self.tab_info)
        self.line_year.setObjectName("line_year")
        self.horizontalLayout_4.addWidget(self.line_year)

        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

    def _create_type_row(self):
        """创建类型选择行"""
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")

        self.label_4 = QtWidgets.QLabel(self.tab_info)
        self.label_4.setMinimumSize(QtCore.QSize(64, 0))
        self.label_4.setMaximumSize(QtCore.QSize(64, 16777215))
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_5.addWidget(self.label_4)

        self.comboBox = QtWidgets.QComboBox(self.tab_info)
        self.comboBox.setObjectName("comboBox")

        # 添加类型选项图标
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("pics/journal.ico"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.comboBox.addItem(icon1, "")

        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("pics/preprint.ico"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.comboBox.addItem(icon2, "")

        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("pics/conference.ico"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.comboBox.addItem(icon3, "")

        self.horizontalLayout_5.addWidget(self.comboBox)

        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

    def _create_publication_row(self):
        """创建期刊/会议输入行"""
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")

        self.label_2 = QtWidgets.QLabel(self.tab_info)
        self.label_2.setEnabled(True)
        self.label_2.setMinimumSize(QtCore.QSize(64, 0))
        self.label_2.setMaximumSize(QtCore.QSize(64, 16777215))
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_6.addWidget(self.label_2)

        self.line_pub = QtWidgets.QLineEdit(self.tab_info)
        self.line_pub.setObjectName("line_pub")
        self.horizontalLayout_6.addWidget(self.line_pub)

        self.verticalLayout_2.addLayout(self.horizontalLayout_6)

    def _create_zky_row(self):
        """创建中科院分区输入行"""
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")

        self.label_5 = QtWidgets.QLabel(self.tab_info)
        self.label_5.setMinimumSize(QtCore.QSize(64, 0))
        self.label_5.setMaximumSize(QtCore.QSize(64, 16777215))
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_7.addWidget(self.label_5)

        self.comboBox_zky = QtWidgets.QComboBox(self.tab_info)
        self.comboBox_zky.setObjectName("line_zky")
        self.comboBox_zky.addItem("XXXXX")
        icon_zky1 = QtGui.QIcon()
        icon_zky1.addPixmap(QtGui.QPixmap("pics/yiqu.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.comboBox_zky.addItem(icon_zky1, "中科院一区")
        icon_zky2 = QtGui.QIcon()
        icon_zky2.addPixmap(QtGui.QPixmap("pics/erqu.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.comboBox_zky.addItem(icon_zky2, "中科院二区")
        icon_zky3 = QtGui.QIcon()
        icon_zky3.addPixmap(QtGui.QPixmap("pics/sanqu.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.comboBox_zky.addItem(icon_zky3, "中科院三区")
        icon_zky4 = QtGui.QIcon()
        icon_zky4.addPixmap(QtGui.QPixmap("pics/siqu.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.comboBox_zky.addItem(icon_zky4, "中科院四区")
        self.horizontalLayout_7.addWidget(self.comboBox_zky)
        self.verticalLayout_2.addLayout(self.horizontalLayout_7)

    def _create_ccf_row(self):
        """创建CCF分区输入行"""
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")

        self.label_6 = QtWidgets.QLabel(self.tab_info)
        self.label_6.setMinimumSize(QtCore.QSize(64, 0))
        self.label_6.setMaximumSize(QtCore.QSize(64, 16777215))
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_8.addWidget(self.label_6)

        self.comboBox_ccf = QtWidgets.QComboBox(self.tab_info)
        self.comboBox_ccf.setObjectName("line_ccf")

        items = ['XXXXX', 'CCFA', 'CCFB', 'CCFC']
        for idx, text in enumerate(items):
            if idx > 0:
                icon_ccf = QtGui.QIcon()
                icon_ccf.addPixmap(QtGui.QPixmap(f"pics/{text.lower()}.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
                self.comboBox_ccf.addItem(icon_ccf, f' ---{text}---')
            else:
                self.comboBox_ccf.addItem(text)

        self.horizontalLayout_8.addWidget(self.comboBox_ccf)

        self.verticalLayout_2.addLayout(self.horizontalLayout_8)

    def _create_jcr_row(self):
        """创建JCR分区输入行"""
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")

        self.label_7 = QtWidgets.QLabel(self.tab_info)
        self.label_7.setMinimumSize(QtCore.QSize(64, 0))
        self.label_7.setMaximumSize(QtCore.QSize(64, 16777215))
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_9.addWidget(self.label_7)

        self.comboBox_jcr = QtWidgets.QComboBox(self.tab_info)
        self.comboBox_jcr.setObjectName("line_jcr")
        items_jcr = ['XXXXX', 'Q1', 'Q2', 'Q3', 'Q4']
        for idx, text in enumerate(items_jcr):
            self.comboBox_jcr.addItem(f' ---{text}---')
        self.horizontalLayout_9.addWidget(self.comboBox_jcr)

        self.verticalLayout_2.addLayout(self.horizontalLayout_9)

    def _create_if_row(self):
        """创建影响因子输入行"""
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")

        self.label_9 = QtWidgets.QLabel(self.tab_info)
        self.label_9.setMinimumSize(QtCore.QSize(64, 0))
        self.label_9.setMaximumSize(QtCore.QSize(64, 16777215))
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_10.addWidget(self.label_9)

        self.line_if = QtWidgets.QLineEdit(self.tab_info)
        self.line_if.setObjectName("line_if")
        self.horizontalLayout_10.addWidget(self.line_if)

        self.verticalLayout_2.addLayout(self.horizontalLayout_10)

    def _create_doi_row(self):
        """创建DOI输入行"""
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")

        self.label_8 = QtWidgets.QLabel(self.tab_info)
        self.label_8.setMinimumSize(QtCore.QSize(64, 0))
        self.label_8.setMaximumSize(QtCore.QSize(64, 16777215))
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_11.addWidget(self.label_8)

        self.line_doi = QtWidgets.QLineEdit(self.tab_info)
        self.line_doi.setObjectName("line_doi")
        self.horizontalLayout_11.addWidget(self.line_doi)

        self.verticalLayout_2.addLayout(self.horizontalLayout_11)

    def _create_url_row(self):
        """创建URL输入行"""
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")

        self.label_10 = QtWidgets.QLabel(self.tab_info)
        self.label_10.setMinimumSize(QtCore.QSize(64, 0))
        self.label_10.setMaximumSize(QtCore.QSize(64, 16777215))
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_12.addWidget(self.label_10)

        self.line_url = QtWidgets.QLineEdit(self.tab_info)
        self.line_url.setObjectName("line_url")
        self.horizontalLayout_12.addWidget(self.line_url)

        self.verticalLayout_2.addLayout(self.horizontalLayout_12)

    def _create_abstract_section(self):
        """创建摘要部分"""
        self.line_3 = QtWidgets.QFrame(self.tab_info)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.verticalLayout_2.addWidget(self.line_3)

        self.label_11 = QtWidgets.QLabel(self.tab_info)
        self.label_11.setObjectName("label_11")
        self.verticalLayout_2.addWidget(self.label_11)

        self.textEdit_abstract = QtWidgets.QTextEdit(self.tab_info)
        self.textEdit_abstract.setObjectName("textEdit_abstract")
        self.verticalLayout_2.addWidget(self.textEdit_abstract)

    def _create_save_button(self):
        """创建保存按钮"""
        self.button_save_info = QtWidgets.QPushButton(self.tab_info)
        self.button_save_info.setMinimumSize(QtCore.QSize(120, 0))
        self.button_save_info.setMaximumSize(QtCore.QSize(120, 16777215))
        self.button_save_info.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.button_save_info.setObjectName("button_save_info")
        self.verticalLayout_2.addWidget(self.button_save_info)

    def _create_menu_bar(self, MainWindow):
        """创建菜单栏"""
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1336, 23))
        self.menubar.setObjectName("menubar")

        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")

        self.menu_2 = QtWidgets.QMenu(self.menubar)
        self.menu_2.setObjectName("menu_2")

        MainWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())

    def _create_toolbar(self, MainWindow):
        """创建工具栏"""
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        self.toolBar.setFont(font)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)

        # 创建工具栏动作
        self._create_toolbar_actions(MainWindow)

        # 添加动作到工具栏
        self.toolBar.addAction(self.action)
        self.toolBar.addAction(self.action_2)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.action_3)
        self.toolBar.addAction(self.action_4)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.action_5)

    def _create_toolbar_actions(self, MainWindow):
        """创建工具栏动作项"""
        # 新建动作
        self.action = QtWidgets.QAction(MainWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("pics/new.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action.setIcon(icon4)
        self.action.setObjectName("action")

        # 打开文件夹动作
        self.action_2 = QtWidgets.QAction(MainWindow)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap("pics/open.ico"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.action_2.setIcon(icon5)
        self.action_2.setObjectName("action_2")

        # 保存动作
        self.action_3 = QtWidgets.QAction(MainWindow)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap("pics/save.ico"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.action_3.setIcon(icon6)
        self.action_3.setObjectName("action_3")

        # 回收站动作
        self.action_4 = QtWidgets.QAction(MainWindow)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap("pics/bin.ico"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.action_4.setIcon(icon7)
        self.action_4.setObjectName("action_4")

        # 搜索动作
        self.action_5 = QtWidgets.QAction(MainWindow)
        font = QtGui.QFont()
        font.setFamily("宋体")
        font.setPointSize(11)
        self.action_5.setFont(font)
        self.action_5.setObjectName("action_5")


    def retranslateUi(self, MainWindow):
        """
        重新翻译UI文本（国际化支持）

        Args:
            MainWindow: 主窗口对象
        """
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "TagLib"))
        self.groupBox.setTitle(_translate("MainWindow", "GroupBox"))
        self.groupBox_2.setTitle(_translate("MainWindow", "GroupBox"))
        self.label.setText(_translate("MainWindow", "标题"))
        self.label_12.setText(_translate("MainWindow", "中文标题"))
        self.label_3.setText(_translate("MainWindow", "年份"))
        self.label_4.setText(_translate("MainWindow", "类型"))
        self.comboBox.setItemText(0, _translate("MainWindow", "Journal paper"))
        self.comboBox.setItemText(1, _translate("MainWindow", "Preprint paper"))
        self.comboBox.setItemText(2, _translate("MainWindow", "Conference paper"))
        self.label_2.setText(_translate("MainWindow", "期刊/会议"))
        self.label_5.setText(_translate("MainWindow", "中科院"))
        self.label_6.setText(_translate("MainWindow", "CCF"))
        self.label_7.setText(_translate("MainWindow", "JCR"))
        self.label_9.setText(_translate("MainWindow", "IF"))
        self.label_8.setText(_translate("MainWindow", "DOI"))
        self.label_10.setText(_translate("MainWindow", "URL"))
        self.label_11.setText(_translate("MainWindow", "Abstract"))
        self.button_save_info.setText(_translate("MainWindow", "保存信息"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_info), _translate("MainWindow", "Info"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Tab 2"))
        self.menu.setTitle(_translate("MainWindow", "编辑"))
        self.menu_2.setTitle(_translate("MainWindow", "关于"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.action.setText(_translate("MainWindow", "新建"))
        self.action.setShortcut(_translate("MainWindow", "Ctrl+N"))
        self.action_2.setText(_translate("MainWindow", "打开文件夹"))
        self.action_3.setText(_translate("MainWindow", "保存"))
        self.action_3.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.action_4.setText(_translate("MainWindow", "回收站"))
        self.action_4.setShortcut(_translate("MainWindow", "Ctrl+D"))
        self.action_5.setText(_translate("MainWindow", "搜索:"))

    def adjust_text_height(self, text_edit=None):
        """
        通用的文本框高度调整槽函数
        根据内容自动调整QTextEdit控件的高度

        Args:
            text_edit: 需要调整高度的QTextEdit控件，如果为None则使用self.text_title
        """
        if text_edit is None:
            text_edit = self.text_title

        # 正确计算内容高度
        document_height = text_edit.document().size().height()
        margins = text_edit.contentsMargins()
        frame_width = text_edit.frameWidth()

        # 设置合适的高度（考虑边距和边框）
        new_height = int(document_height) + margins.top() + margins.bottom() + 2 * frame_width
        text_edit.setFixedHeight(min(new_height, 50))  # 设置最小高度为50
