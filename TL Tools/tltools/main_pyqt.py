# _*_ coding:utf-8 _*_
# @File  : 拖拽表格.py
# @Time  : 2021-05-10 15:42
# @Author: zizle
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QBrush, QColor, QPalette, QPixmap
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, QWidget, QHBoxLayout, QLabel, QPushButton

# 导入 MeasurementData 类
from data_oop import MeasurementData

class DraggableTableWidget(QTableWidget):
    def __init__(self,path, *args, **kwargs):
        super(DraggableTableWidget, self).__init__(*args, **kwargs)
        self.resize(800, 450)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.data_keys = ["文件名", "测站", "目标", "归零方向均值", "天顶角均值", "斜距"]
        self.setHorizontalHeaderLabels(self.data_keys) # 设置表头
        self.path = path
        self.drag_row = -1
        self.drop_row = None
        self.drag_widget = None
        self.init_drag_widget()

    def set_drag_data_on_widget(self, row_data): # 设置拖拽的数据
        drag_layout = QHBoxLayout(self.drag_widget) # 水平布局
        drag_layout.setContentsMargins(10, 0, 0, 0) # 设置布局的边距
        for col in range(self.columnCount()): # 遍历列
            text_label = QLabel(str(row_data[col]), self.drag_widget) # 创建标签
            text_label.setFixedWidth(self.columnWidth(col)) # 设置标签的宽度
            text_label.setAlignment(Qt.AlignCenter) # 设置标签的对齐方式
            drag_layout.addWidget(text_label) # 添加标签到布局
            button = QPushButton(self)  # 创建按钮
            button.setFocusPolicy(Qt.NoFocus) # 设置按钮的焦点策略
            button.setFixedWidth(1) # 设置按钮的宽度
            drag_layout.addWidget(button) # 添加按钮到布局
        drag_layout.addStretch() # 添加伸缩空间
        self.drag_widget.setLayout(drag_layout) # 设置布局
        setattr(self.drag_widget, 'row_data', row_data) # 设置属性

    def init_drag_widget(self):
        if self.drag_widget is not None and isinstance(self.drag_widget, QWidget): # 如果拖拽窗口存在
            self.drag_widget.deleteLater() # 删除拖拽窗口
            self.drag_widget = None # 重置拖拽窗口
        self.drag_widget = QWidget(self) # 创建拖拽窗口
        p = self.drag_widget.palette() # 获取拖拽窗口的调色板
        p.setColor(QPalette.Background, QColor(0, 200, 100)) # 设置拖拽窗口的背景颜色
        self.drag_widget.setPalette(p) # 设置拖拽窗口的调色板
        self.drag_widget.setAutoFillBackground(True) # 设置拖拽窗口自动填充背景
        self.drag_widget.resize(self.width(), 30) # 设置拖拽窗口的大小
        self.drag_widget.hide() # 隐藏拖拽窗口




    def mouseMoveEvent(self, event) -> None:
        self.drag_widget.move(event.pos()) # 设置拖拽窗口的位置
        self.drag_widget.show() # 显示拖拽窗口
        row, col = self.indexAt(event.pos()).row(), self.indexAt(event.pos()).column() # 获取鼠标位置的行和列
        print(row, col) # 打印行和列
        self.set_row_bg_color(row, QColor(254, 163, 86)) # 设置行的背景颜色
        self.set_row_bg_color(row + 1, QColor(255, 255, 255)) # 设置行的背景颜色
        self.set_row_bg_color(row - 1, QColor(255, 255, 255)) # 设置行的背景颜色

    def set_row_bg_color(self, row, color):
        if row < 0:
            return
        for col in range(self.columnCount()): # 遍历列
            item = self.item(row, col) # 获取单元格
            if item: # 如果单元格存在
                item.setBackground(QBrush(color)) # 设置单元格的背景颜色

    def mousePressEvent(self, event) -> None: # 鼠标按下事件
        row, col = self.indexAt(event.pos()).row(), self.indexAt(event.pos()).column() # 获取鼠标位置的行和列
        cur_item = self.item(row, col) # 获取当前单元格
        if col == 0 and cur_item: # 如果点击的是第一列 并且单元格存在
            drag_row_data = cur_item.data(Qt.UserRole) # 获取第一列的数据
            self.set_drag_data_on_widget(drag_row_data) # 设置拖拽的数据
            self.drag_row = row # 设置拖拽的行
            super(DraggableTableWidget, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        row, col = self.indexAt(event.pos()).row(), self.indexAt(event.pos()).column() # 获取鼠标位置的行和列
        self.set_row_bg_color(row, QColor(255, 255, 255)) # 设置行的背景颜色
        # self.removeRow(self.drag_row) # 移除拖拽的行
        row_data = getattr(self.drag_widget, 'row_data', None) # 获取拖拽窗口的数据
        if row_data: # 如果数据存在
            self.removeRow(self.drag_row)  # 移除拖拽的行
            self.insert_row_data(row, row_data) # 插入行数据
            self.selectRow(row) # 选中行
        self.init_drag_widget() # 初始化拖拽窗口
        super(DraggableTableWidget, self).mouseReleaseEvent(event)

    def get_table_data(self):
        # 从外部文件生成数据
        data_instance = MeasurementData(self.path)
        return data_instance.transform_data

    def set_data(self):
        self.setColumnCount(len(self.data_keys))
        self.setHorizontalHeaderLabels(self.data_keys)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        for row, row_item in enumerate(self.get_table_data()):
            self.insert_row_data(row, row_item)

    def insert_row_data(self, row, row_item):
        self.insertRow(row)
        for col, value in enumerate(row_item):
            item = QTableWidgetItem(str(value))
            if col == 0:
                item.setData(Qt.UserRole, row_item)
            self.setItem(row, col, item)

app = QApplication([])
path = 'D:/tl_tools/data/原始数据/test/20240624-1'
t = DraggableTableWidget(path)
t.set_data()
t.show()
sys.exit(app.exec_())
