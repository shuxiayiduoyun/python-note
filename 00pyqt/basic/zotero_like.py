#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：python-note 
@File    ：zotero_like.py
@IDE     ：PyCharm 
@Author  ：wei liyu
@Date    ：2025/10/16 11:25 
'''
# -*- coding: utf-8 -*-
"""
Zotero-like 文献管理 UI（PyQt 5.15）
- 三栏布局：集合树 / 文献表 / 详情面板（Info/Notes/Tags/Related）
- 搜索、排序、集合/标签过滤、回收站
- 可编辑详情并回写内存数据
- QSettings 持久化窗口状态

运行：
    pip install PyQt5==5.15.10
    python zotero_like_ui.py
"""

import sys
import uuid
from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets


# ========== 业务数据层（内存示例，可换成你的存储） ==========
def _now_iso():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def _uid():
    return uuid.uuid4().hex[:8]


class LibraryData(QtCore.QObject):
    """
    简单的内存数据层：items / collections / tags
    item 字段推荐：
      id, title, creators(list[str]), year, venue, type, tags(list[str]),
      abstract, doi, url, date_added, collections(set[str]), trashed(bool), notes(str)
    """
    data_changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.collections = {}  # id -> dict(name, parent)
        self.items = {}        # id -> dict(...)
        self.root_id = "root"
        self.trash_id = "trash"
        self._init_demo()

    # ---- 初始化一些演示数据 ----
    def _init_demo(self):
        self.collections[self.root_id] = {"id": self.root_id, "name": "我的文库", "parent": None}
        self.collections[self.trash_id] = {"id": self.trash_id, "name": "回收站", "parent": None}

        c_ml = self.add_collection("机器学习")
        c_proj = self.add_collection("项目A")
        c_read = self.add_collection("阅读清单")

        demo_items = [
            dict(
                id=_uid(),
                title="Attention Is All You Need",
                creators=["Vaswani, A.", "Shazeer, N.", "Parmar, N."],
                year="2017",
                venue="NeurIPS",
                type="Conference Paper",
                tags=["transformer", "nlp"],
                abstract="提出 Transformer 架构，使用自注意力机制替代循环和卷积。",
                doi="10.5555/3295222.3295349",
                url="https://arxiv.org/abs/1706.03762",
                date_added=_now_iso(),
                collections={c_ml, c_read},
                trashed=False,
                notes="核心思想是自注意力 + 多头 + 残差 + 层归一化。",
            ),
            dict(
                id=_uid(),
                title="BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
                creators=["Devlin, J.", "Chang, M.-W.", "Lee, K.", "Toutanova, K."],
                year="2019",
                venue="NAACL",
                type="Conference Paper",
                tags=["bert", "nlp", "pretraining"],
                abstract="双向 Transformer 的掩码语言模型预训练。",
                doi="",
                url="https://arxiv.org/abs/1810.04805",
                date_added=_now_iso(),
                collections={c_ml},
                trashed=False,
                notes="",
            ),
            dict(
                id=_uid(),
                title="A Gentle Introduction to Monte Carlo Dropout",
                creators=["Gal, Y."],
                year="2016",
                venue="Blog",
                type="Article",
                tags=["uncertainty", "dropout"],
                abstract="用 Dropout 进行贝叶斯近似，估计模型不确定性。",
                doi="",
                url="",
                date_added=_now_iso(),
                collections={c_proj},
                trashed=False,
                notes="结合 ResNet 可在 fc 前添加 dropout；推理阶段开启。",
            ),
            dict(
                id=_uid(),
                title="ResNet: Deep Residual Learning for Image Recognition",
                creators=["He, K.", "Zhang, X.", "Ren, S.", "Sun, J."],
                year="2016",
                venue="CVPR",
                type="Conference Paper",
                tags=["resnet", "cv"],
                abstract="残差连接缓解退化问题，极大提升深层网络可训练性。",
                doi="",
                url="",
                date_added=_now_iso(),
                collections={c_ml},
                trashed=False,
                notes="",
            ),
        ]
        for it in demo_items:
            self.items[it["id"]] = it

    # ---- 集合 ----
    def add_collection(self, name, parent=None):
        cid = _uid()
        self.collections[cid] = {"id": cid, "name": name, "parent": parent}
        self.data_changed.emit()
        return cid

    # ---- 文献 ----
    def add_item(self, **kwargs):
        it = dict(
            id=_uid(),
            title=kwargs.get("title", "未命名条目"),
            creators=kwargs.get("creators", []),
            year=kwargs.get("year", ""),
            venue=kwargs.get("venue", ""),
            type=kwargs.get("type", "Article"),
            tags=kwargs.get("tags", []),
            abstract=kwargs.get("abstract", ""),
            doi=kwargs.get("doi", ""),
            url=kwargs.get("url", ""),
            date_added=_now_iso(),
            collections=set(kwargs.get("collections", [])),
            trashed=False,
            notes=kwargs.get("notes", ""),
        )
        self.items[it["id"]] = it
        self.data_changed.emit()
        return it["id"]

    def update_item(self, item_id, fields: dict):
        if item_id in self.items:
            self.items[item_id].update(fields)
            self.data_changed.emit()

    def trash_item(self, item_id, to_trash=True):
        if item_id in self.items:
            self.items[item_id]["trashed"] = bool(to_trash)
            self.data_changed.emit()

    def delete_item_permanently(self, item_id):
        if item_id in self.items:
            del self.items[item_id]
            self.data_changed.emit()

    def get_all_tags(self):
        tags = set()
        for it in self.items.values():
            if not it["trashed"]:
                tags.update(it["tags"])
        return sorted(tags)


# ========== 表格模型 & 过滤 ==========
class ItemTableModel(QtCore.QAbstractTableModel):
    COLS = ["类型", "标题", "作者", "年份", "期刊/会议", "标签", "添加时间"]

    def __init__(self, library: LibraryData, parent=None):
        super().__init__(parent)
        self.library = library
        self.ids = list(library.items.keys())
        library.data_changed.connect(self._rebuild_ids)

    def _rebuild_ids(self):
        self.beginResetModel()
        self.ids = list(self.library.items.keys())
        self.endResetModel()

    # ---- 核心表格接口 ----
    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.ids)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.COLS)

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return self.COLS[section]
        return super().headerData(section, orientation, role)

    def item_for_row(self, row):
        item_id = self.ids[row]
        return self.library.items[item_id]

    def data(self, index, role):
        if not index.isValid():
            return None
        item = self.item_for_row(index.row())
        col = index.column()

        if role == QtCore.Qt.DisplayRole:
            if col == 0:
                return item["type"]
            elif col == 1:
                return item["title"]
            elif col == 2:
                return ", ".join(item["creators"])
            elif col == 3:
                return item["year"]
            elif col == 4:
                return item["venue"]
            elif col == 5:
                return ", ".join(item["tags"])
            elif col == 6:
                return item["date_added"]

        if role == QtCore.Qt.DecorationRole and col == 0:
            style = QtWidgets.QApplication.style()
            return style.standardIcon(QtWidgets.QStyle.SP_FileIcon)

        # 更稳定的排序键
        if role == QtCore.Qt.UserRole:
            if col == 3:
                try:
                    return int(item["year"])
                except Exception:
                    return 0
            elif col == 6:
                return item["date_added"]
            else:
                return str(self.data(index, QtCore.Qt.DisplayRole) or "")

        # 保存 item_id 便于外部检索
        if role == QtCore.Qt.UserRole + 1:
            return item["id"]

        return None

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled


class ItemFilterProxy(QtCore.QSortFilterProxyModel):
    """
    支持：搜索（标题/作者/标签/DOI/URL）、集合过滤、标签过滤、回收站视图
    """
    def __init__(self, library: LibraryData, parent=None):
        super().__init__(parent)
        self.library = library
        self.search_text = ""
        self.active_collection = "root"
        self.active_tags = set()  # 选中的标签（AND 关系）
        self.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setDynamicSortFilter(True)

    def set_search(self, text: str):
        self.search_text = text.strip()
        self.invalidateFilter()

    def set_collection(self, cid: str):
        self.active_collection = cid
        self.invalidateFilter()

    def set_active_tags(self, tags: set):
        self.active_tags = set(tags)
        self.invalidateFilter()

    def lessThan(self, left, right):
        # 默认用 UserRole 的“稳定键”排序
        l = self.sourceModel().data(left, QtCore.Qt.UserRole)
        r = self.sourceModel().data(right, QtCore.Qt.UserRole)
        return str(l) < str(r)

    def filterAcceptsRow(self, source_row, source_parent):
        model: ItemTableModel = self.sourceModel()
        idx0 = model.index(source_row, 0, source_parent)
        item_id = model.data(idx0, QtCore.Qt.UserRole + 1)
        it = self.library.items.get(item_id, None)
        if not it:
            return False

        # 1) 回收站视图
        if self.active_collection == "trash":
            if not it["trashed"]:
                return False
        else:
            if it["trashed"]:
                return False

        # 2) 集合过滤
        if self.active_collection not in ("root", "trash"):
            if self.active_collection not in it["collections"]:
                return False

        # 3) 标签（AND）
        if self.active_tags:
            if not set(self.active_tags).issubset(set(it["tags"])):
                return False

        # 4) 搜索（标题 / 作者 / 标签 / doi / url / venue）
        if self.search_text:
            q = self.search_text.lower()
            hay = " ".join([
                it["title"],
                ", ".join(it["creators"]),
                ", ".join(it["tags"]),
                it.get("doi", ""),
                it.get("url", ""),
                it.get("venue", ""),
            ]).lower()
            if q not in hay:
                return False

        return True


# ========== 右侧详情面板 ==========
class RightPanel(QtWidgets.QWidget):
    request_refresh = QtCore.pyqtSignal()  # 编辑后通知刷新

    def __init__(self, library: LibraryData, parent=None):
        super().__init__(parent)
        self.library = library
        self.current_id = None

        tabs = QtWidgets.QTabWidget(self)

        # --- Info tab ---
        self.title = QtWidgets.QLineEdit()
        self.creators = QtWidgets.QLineEdit()
        self.year = QtWidgets.QLineEdit()
        self.venue = QtWidgets.QLineEdit()
        self.type = QtWidgets.QComboBox()
        self.type.addItems(["Article", "Conference Paper", "Preprint", "Thesis", "Book"])
        self.doi = QtWidgets.QLineEdit()
        self.url = QtWidgets.QLineEdit()
        self.abstract = QtWidgets.QTextEdit()
        self.abstract.setMinimumHeight(120)

        form = QtWidgets.QFormLayout()
        form.addRow("标题", self.title)
        form.addRow("作者（逗号分隔）", self.creators)
        form.addRow("年份", self.year)
        form.addRow("期刊/会议", self.venue)
        form.addRow("类型", self.type)
        form.addRow("DOI", self.doi)
        form.addRow("URL", self.url)
        form.addRow("摘要", self.abstract)

        btn_save = QtWidgets.QPushButton("保存信息")
        btn_reset = QtWidgets.QPushButton("重置")
        btn_box = QtWidgets.QHBoxLayout()
        btn_box.addStretch(1)
        btn_box.addWidget(btn_reset)
        btn_box.addWidget(btn_save)

        info_wrap = QtWidgets.QWidget()
        info_lay = QtWidgets.QVBoxLayout(info_wrap)
        info_lay.addLayout(form)
        info_lay.addLayout(btn_box)
        info_lay.addStretch(1)

        # --- Notes tab ---
        self.notes = QtWidgets.QTextEdit()
        btn_notes = QtWidgets.QPushButton("保存笔记")
        notes_wrap = QtWidgets.QWidget()
        notes_lay = QtWidgets.QVBoxLayout(notes_wrap)
        notes_lay.addWidget(self.notes)
        notes_lay.addWidget(btn_notes)

        # --- Tags tab ---
        self.tag_input = QtWidgets.QLineEdit()
        self.tag_input.setPlaceholderText("输入标签按 Enter 添加")
        self.tag_list = QtWidgets.QListWidget()
        self.tag_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        btn_del_tag = QtWidgets.QPushButton("删除选中标签")

        tags_wrap = QtWidgets.QWidget()
        tags_lay = QtWidgets.QVBoxLayout(tags_wrap)
        tags_lay.addWidget(self.tag_input)
        tags_lay.addWidget(self.tag_list)
        tags_lay.addWidget(btn_del_tag)

        # --- Related tab (占位) ---
        self.related = QtWidgets.QListWidget()
        related_wrap = QtWidgets.QWidget()
        related_lay = QtWidgets.QVBoxLayout(related_wrap)
        related_lay.addWidget(QtWidgets.QLabel("（占位）在此显示相关条目"))
        related_lay.addWidget(self.related)

        tabs.addTab(info_wrap, "Info")
        tabs.addTab(notes_wrap, "Notes")
        tabs.addTab(tags_wrap, "Tags")
        tabs.addTab(related_wrap, "Related")

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(tabs)

        # 绑定事件
        btn_save.clicked.connect(self._save_info)
        btn_reset.clicked.connect(self._reload)
        btn_notes.clicked.connect(self._save_notes)
        self.tag_input.returnPressed.connect(self._add_tag)
        btn_del_tag.clicked.connect(self._delete_selected_tags)

    # ---- 对外接口 ----
    def show_item(self, item_id: str):
        self.current_id = item_id
        self._reload()

    # ---- 内部操作 ----
    def _reload(self):
        it = self.library.items.get(self.current_id)
        if not it:
            self._clear()
            return
        self.title.setText(it["title"])
        self.creators.setText(", ".join(it["creators"]))
        self.year.setText(it["year"])
        self.venue.setText(it["venue"])
        ix = max(0, self.type.findText(it["type"]))
        self.type.setCurrentIndex(ix)
        self.doi.setText(it.get("doi", ""))
        self.url.setText(it.get("url", ""))
        self.abstract.setPlainText(it.get("abstract", ""))
        self.notes.setPlainText(it.get("notes", ""))

        self.tag_list.clear()
        for t in it["tags"]:
            self.tag_list.addItem(t)

    def _clear(self):
        for w in [self.title, self.creators, self.year, self.venue, self.doi, self.url]:
            w.clear()
        self.abstract.clear()
        self.notes.clear()
        self.tag_list.clear()

    def _save_info(self):
        if not self.current_id:
            return
        creators = [x.strip() for x in self.creators.text().split(",") if x.strip()]
        self.library.update_item(self.current_id, dict(
            title=self.title.text().strip(),
            creators=creators,
            year=self.year.text().strip(),
            venue=self.venue.text().strip(),
            type=self.type.currentText(),
            doi=self.doi.text().strip(),
            url=self.url.text().strip(),
            abstract=self.abstract.toPlainText().strip(),
        ))
        self.request_refresh.emit()

    def _save_notes(self):
        if not self.current_id:
            return
        self.library.update_item(self.current_id, dict(
            notes=self.notes.toPlainText().strip()
        ))
        self.request_refresh.emit()

    def _add_tag(self):
        if not self.current_id:
            return
        new_tag = self.tag_input.text().strip()
        if not new_tag:
            return
        it = self.library.items[self.current_id]
        if new_tag not in it["tags"]:
            it["tags"].append(new_tag)
            self.library.data_changed.emit()
            self.tag_input.clear()
            self._reload()
            self.request_refresh.emit()

    def _delete_selected_tags(self):
        if not self.current_id:
            return
        it = self.library.items[self.current_id]
        selected = [i.text() for i in self.tag_list.selectedItems()]
        if not selected:
            return
        it["tags"] = [t for t in it["tags"] if t not in selected]
        self.library.data_changed.emit()
        self._reload()
        self.request_refresh.emit()


# ========== 左侧集合树 & 标签过滤器 ==========
class CollectionTree(QtWidgets.QTreeView):
    collection_changed = QtCore.pyqtSignal(str)

    def __init__(self, library: LibraryData, parent=None):
        super().__init__(parent)
        self.library = library
        self.setHeaderHidden(True)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.model_m = QtGui.QStandardItemModel()
        self.setModel(self.model_m)

        self._build_tree()
        library.data_changed.connect(self._build_tree)
        self.selectionModel().selectionChanged.connect(self._emit_current)

    def _build_tree(self):
        self.model_m.clear()
        root = self.model_m.invisibleRootItem()

        def make_item(text, cid, icon=None):
            item = QtGui.QStandardItem(text)
            item.setData(cid, QtCore.Qt.UserRole)
            item.setEditable(False)
            if icon:
                item.setIcon(icon)
            return item

        style = QtWidgets.QApplication.style()
        lib_icon = style.standardIcon(QtWidgets.QStyle.SP_DirHomeIcon)
        trash_icon = style.standardIcon(QtWidgets.QStyle.SP_TrashIcon)
        folder_icon = style.standardIcon(QtWidgets.QStyle.SP_DirIcon)

        lib_item = make_item(self.library.collections[self.library.root_id]["name"],
                             self.library.root_id, lib_icon)
        trash_item = make_item(self.library.collections[self.library.trash_id]["name"],
                               self.library.trash_id, trash_icon)

        # 平铺所有自建集合（无层级关系的简化，想做层级可递归 parent 字段）
        for cid, c in self.library.collections.items():
            if cid in (self.library.root_id, self.library.trash_id):
                continue
            lib_item.appendRow(make_item(c["name"], cid, folder_icon))

        root.appendRow(lib_item)
        root.appendRow(trash_item)
        self.expandAll()
        # 默认选中“我的文库”
        idx = self.model_m.indexFromItem(lib_item)
        self.setCurrentIndex(idx)

    def _emit_current(self, *args):
        idx = self.currentIndex()
        if not idx.isValid():
            return
        cid = self.model().itemFromIndex(idx).data(QtCore.Qt.UserRole)
        if cid:
            self.collection_changed.emit(cid)

    # 方便从外部获取当前集合 id
    def current_collection_id(self):
        idx = self.currentIndex()
        if not idx.isValid():
            return "root"
        return self.model().itemFromIndex(idx).data(QtCore.Qt.UserRole)


class TagFilter(QtWidgets.QGroupBox):
    tags_changed = QtCore.pyqtSignal(set)

    def __init__(self, library: LibraryData, parent=None):
        super().__init__("标签过滤", parent)
        self.library = library
        self.listw = QtWidgets.QListWidget()
        self.listw.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(self.listw)

        self.refresh()
        library.data_changed.connect(self.refresh)
        self.listw.itemSelectionChanged.connect(self._emit)

    def refresh(self):
        sel = {i.text() for i in self.listw.selectedItems()}
        self.listw.clear()
        for t in self.library.get_all_tags():
            self.listw.addItem(t)
        # 保留原选中（如果仍存在）
        for i in range(self.listw.count()):
            it = self.listw.item(i)
            it.setSelected(it.text() in sel)

    def _emit(self):
        tags = {i.text() for i in self.listw.selectedItems()}
        self.tags_changed.emit(tags)


# ========== 主窗口 ==========
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zotero-like 文献管理示例（PyQt 5.15）")
        self.resize(1200, 720)
        self.setUnifiedTitleAndToolBarOnMac(True)

        # 数据层
        self.library = LibraryData(self)

        # 中央三栏 splitter
        splitter = QtWidgets.QSplitter()
        splitter.setHandleWidth(6)
        self.setCentralWidget(splitter)

        # 左：集合树 + 标签过滤
        left_split = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.coll_tree = CollectionTree(self.library)
        self.tag_filter = TagFilter(self.library)
        left_split.addWidget(self.coll_tree)
        left_split.addWidget(self.tag_filter)
        left_split.setStretchFactor(0, 3)
        left_split.setStretchFactor(1, 2)

        # 中：表格
        self.table_model = ItemTableModel(self.library)
        self.proxy = ItemFilterProxy(self.library)
        self.proxy.setSourceModel(self.table_model)

        self.table = QtWidgets.QTableView()
        self.table.setModel(self.proxy)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.table.setSortingEnabled(True)
        self.table.sortByColumn(6, QtCore.Qt.DescendingOrder)
        self.table.verticalHeader().setVisible(False)
        hh = self.table.horizontalHeader()
        hh.setStretchLastSection(True)
        hh.setSectionsMovable(True)
        hh.setSectionResizeMode(QtWidgets.QHeaderView.Interactive)

        # 右：详情面板
        self.detail = RightPanel(self.library)

        # 装进 splitter
        splitter.addWidget(left_split)
        splitter.addWidget(self.table)
        splitter.addWidget(self.detail)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)

        # 顶部工具栏 & 搜索
        self._build_actions_and_toolbar()

        # 状态栏
        self.status = QtWidgets.QStatusBar()
        self.setStatusBar(self.status)
        self.count_label = QtWidgets.QLabel("0 项")
        self.status.addPermanentWidget(self.count_label)

        # 信号互联
        self.coll_tree.collection_changed.connect(self._on_collection_changed)
        self.tag_filter.tags_changed.connect(self._on_tags_changed)
        self.table.selectionModel().selectionChanged.connect(self._on_row_selected)
        self.detail.request_refresh.connect(self._refresh_views)
        self.library.data_changed.connect(self._refresh_views)

        # 恢复状态
        self._restore_state()
        # 首次计数刷新
        self._refresh_counter()

        # 默认选中第一行
        QtCore.QTimer.singleShot(0, self._select_first_row)

    # ---- 构建动作 & 工具栏 ----
    def _build_actions_and_toolbar(self):
        style = self.style()

        act_new_item = QtWidgets.QAction(style.standardIcon(QtWidgets.QStyle.SP_FileIcon), "新建文献", self)
        act_new_item.setShortcut("Ctrl+N")
        act_new_item.triggered.connect(self._new_item)

        act_new_col = QtWidgets.QAction(style.standardIcon(QtWidgets.QStyle.SP_DirIcon), "新建集合", self)
        act_new_col.setShortcut("Ctrl+Shift+N")
        act_new_col.triggered.connect(self._new_collection)

        act_edit = QtWidgets.QAction(style.standardIcon(QtWidgets.QStyle.SP_FileDialogDetailedView), "编辑", self)
        act_edit.setShortcut("Ctrl+E")
        act_edit.triggered.connect(self._focus_detail)

        act_trash = QtWidgets.QAction(style.standardIcon(QtWidgets.QStyle.SP_TrashIcon), "移入回收站", self)
        act_trash.setShortcut("Del")
        act_trash.triggered.connect(self._to_trash)

        act_restore = QtWidgets.QAction("从回收站还原", self)
        act_restore.triggered.connect(self._restore_from_trash)

        act_delete_perm = QtWidgets.QAction("永久删除", self)
        act_delete_perm.triggered.connect(self._delete_permanently)

        act_import = QtWidgets.QAction(style.standardIcon(QtWidgets.QStyle.SP_DialogOpenButton), "导入…", self)
        act_export = QtWidgets.QAction(style.standardIcon(QtWidgets.QStyle.SP_DialogSaveButton), "导出…", self)

        self.act_dark = QtWidgets.QAction("深色模式", self, checkable=True)
        self.act_dark.triggered.connect(self._toggle_dark)

        # 搜索框（防抖）
        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setFixedWidth(260)
        self.search_edit.setPlaceholderText("搜索 标题/作者/标签/DOI/URL…")
        self.search_timer = QtCore.QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(250)
        self.search_edit.textChanged.connect(lambda: self.search_timer.start())
        self.search_timer.timeout.connect(self._apply_search)

        tb = self.addToolBar("Main")
        tb.setMovable(False)
        tb.addAction(act_new_item)
        tb.addAction(act_new_col)
        tb.addSeparator()
        tb.addAction(act_edit)
        tb.addAction(act_trash)
        tb.addSeparator()
        tb.addAction(act_import)
        tb.addAction(act_export)
        tb.addSeparator()
        tb.addWidget(QtWidgets.QLabel(" 搜索："))
        tb.addWidget(self.search_edit)
        tb.addSeparator()
        tb.addAction(self.act_dark)

        # 右键菜单（表格）
        self.table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        def ctx_menu(pos):
            menu = QtWidgets.QMenu(self)
            menu.addAction(act_edit)
            if self.coll_tree.current_collection_id() == "trash":
                menu.addAction(act_restore)
                menu.addAction(act_delete_perm)
            else:
                menu.addAction(act_trash)
            menu.exec_(self.table.viewport().mapToGlobal(pos))
        self.table.customContextMenuRequested.connect(ctx_menu)

        # 菜单栏（可选）
        menu_file = self.menuBar().addMenu("文件")
        menu_file.addAction(act_import)
        menu_file.addAction(act_export)
        menu_file.addSeparator()
        exit_action = QtWidgets.QAction("退出", self)
        exit_action.triggered.connect(self.close)
        menu_file.addAction(exit_action)

        menu_edit = self.menuBar().addMenu("编辑")
        menu_edit.addAction(act_new_item)
        menu_edit.addAction(act_new_col)
        menu_edit.addAction(act_edit)
        menu_edit.addAction(act_trash)

        menu_view = self.menuBar().addMenu("视图")
        menu_view.addAction(self.act_dark)

    # ---- 状态保存/恢复 ----
    def _restore_state(self):
        s = QtCore.QSettings("ZoteroLike", "PaperManager")
        if g := s.value("geometry"):
            self.restoreGeometry(g)
        if st := s.value("windowState"):
            self.restoreState(st)
        # 列宽
        if self.table.model():
            hh = self.table.horizontalHeader()
            for i in range(self.table.model().columnCount()):
                w = int(s.value(f"colw_{i}", 0))
                if w > 0:
                    hh.resizeSection(i, w)

    def closeEvent(self, e: QtGui.QCloseEvent):
        s = QtCore.QSettings("ZoteroLike", "PaperManager")
        s.setValue("geometry", self.saveGeometry())
        s.setValue("windowState", self.saveState())
        # 列宽
        if self.table.model():
            hh = self.table.horizontalHeader()
            for i in range(self.table.model().columnCount()):
                s.setValue(f"colw_{i}", hh.sectionSize(i))
        super().closeEvent(e)

    # ---- 交互逻辑 ----
    def _apply_search(self):
        self.proxy.set_search(self.search_edit.text())
        self._refresh_counter()

    def _on_collection_changed(self, cid: str):
        self.proxy.set_collection(cid)
        self._refresh_counter()

    def _on_tags_changed(self, tags: set):
        self.proxy.set_active_tags(tags)
        self._refresh_counter()

    def _on_row_selected(self, *args):
        idxs = self.table.selectionModel().selectedRows()
        if not idxs:
            self.detail.show_item(None)
            return
        # 显示第一条
        src = self.proxy.mapToSource(idxs[0])
        item_id = self.table_model.data(src, QtCore.Qt.UserRole + 1)
        self.detail.show_item(item_id)

    def _refresh_views(self):
        # 刷新 tag 列表和计数
        self.tag_filter.refresh()
        self._refresh_counter()
        self.table.repaint()

    def _refresh_counter(self):
        self.count_label.setText(f"{self.proxy.rowCount()} 项")

    def _select_first_row(self):
        if self.proxy.rowCount() > 0:
            self.table.selectRow(0)

    def _focus_detail(self):
        self.detail.setFocus()

    def _current_selected_ids(self):
        ids = []
        for idx in self.table.selectionModel().selectedRows():
            src = self.proxy.mapToSource(idx)
            ids.append(self.table_model.data(src, QtCore.Qt.UserRole + 1))
        return ids

    def _new_item(self):
        # 在当前集合下快速创建一条空白条目
        coll = self.coll_tree.current_collection_id()
        collections = [] if coll in ("root", "trash") else [coll]
        new_id = self.library.add_item(
            title="新建条目",
            creators=[],
            year="",
            venue="",
            type="Article",
            tags=[],
            abstract="",
            doi="",
            url="",
            collections=collections,
        )
        # 定位并选中
        self.search_edit.clear()
        self.proxy.invalidate()
        self._refresh_counter()
        # 找到新条目所在的行
        for r in range(self.proxy.rowCount()):
            idx = self.proxy.index(r, 1)  # 标题列
            src = self.proxy.mapToSource(idx)
            item_id = self.table_model.data(src, QtCore.Qt.UserRole + 1)
            if item_id == new_id:
                self.table.selectRow(r)
                self.table.scrollTo(self.proxy.index(r, 0))
                break

    def _new_collection(self):
        name, ok = QtWidgets.QInputDialog.getText(self, "新建集合", "输入集合名称：")
        if not ok or not name.strip():
            return
        self.library.add_collection(name.strip())

    def _to_trash(self):
        ids = self._current_selected_ids()
        if not ids:
            return
        for i in ids:
            self.library.trash_item(i, True)
        self._refresh_views()

    def _restore_from_trash(self):
        ids = self._current_selected_ids()
        for i in ids:
            self.library.trash_item(i, False)
        self._refresh_views()

    def _delete_permanently(self):
        ids = self._current_selected_ids()
        if not ids:
            return
        ret = QtWidgets.QMessageBox.question(self, "永久删除",
                                             f"确定永久删除选中的 {len(ids)} 项？此操作不可撤销。",
                                             QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if ret == QtWidgets.QMessageBox.Yes:
            for i in ids:
                self.library.delete_item_permanently(i)
        self._refresh_views()

    # ---- 深色模式（简单版）----
    def _toggle_dark(self, checked):
        app = QtWidgets.QApplication.instance()
        if checked:
            dark = QtGui.QPalette()
            dark.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
            dark.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
            dark.setColor(QtGui.QPalette.Base, QtGui.QColor(35, 35, 35))
            dark.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
            dark.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
            dark.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
            dark.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
            dark.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
            dark.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
            dark.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
            dark.setColor(QtGui.QPalette.Highlight, QtGui.QColor(64, 128, 255))
            dark.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
            app.setPalette(dark)
        else:
            app.setPalette(app.style().standardPalette())


def main():
    QtCore.QCoreApplication.setOrganizationName("ZoteroLike")
    QtCore.QCoreApplication.setApplicationName("PaperManager")
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
