# _*_ coding:utf-8 _*_
# @File  : 拖拽表格.py
# @Time  : 2024/8/28
# @Author: zuo

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QPalette
from PyQt5.QtWidgets import (QTableWidget, QTableWidgetItem,
                             QAbstractItemView, QHeaderView, QWidget,
                             QPushButton, QLabel, QHBoxLayout)

# 定义颜色常量，方便后续维护和修改
HIGHLIGHT_COLOR = QColor(254, 163, 86)
DEFAULT_COLOR = QColor(255, 255, 255)

# 文件名、目标列索引常量，避免硬编码
FILE_COLUMN_INDEX = 1
TARGET_COLUMN_INDEX = 2


class DraggableTableWidget(QTableWidget):
    def __init__(self, grouped_data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        # 表头数据
        self.data_keys = ["上一个", "文件名", "测站", "目标", "归零方向均值", "天顶角均值", "斜距", "仪器高(m)",
                          "目标高(m)",
                          "测站温度", "目标温度", "测站气压", "目标气压", "下一个"]
        self.drag_keys = ["文件名", "测站", "目标", "归零方向均值", "天顶角均值", "斜距", "仪器高(m)", "目标高(m)",
                          "测站温度", "目标温度", "测站气压", "目标气压"]
        self.setHorizontalHeaderLabels(self.data_keys)  # 设置表头

        self.grouped_data = grouped_data

        self.current_indices = {key: 0 for key in self.grouped_data}
        self.cur_key = None  # 当前拖拽的键
        self.drag_row = -1  # 拖拽行的标识
        self.drag_widget = None  # 拖拽的窗口组件
        self.init_drag_widget()  # 初始化拖拽窗口
        self.set_data()  # 初始化表格数据

    def init_drag_widget(self):
        """初始化拖拽窗口组件"""
        if self.drag_widget:
            self.drag_widget.deleteLater()  # 清除旧的拖拽组件
        self.drag_widget = QWidget(self)  # 新建拖拽组件
        self.drag_widget.setAutoFillBackground(True)
        self.drag_widget.setPalette(self._get_drag_widget_palette())  # 设置背景色
        self.drag_widget.resize(self.width(), 30)  # 设置拖拽组件尺寸
        self.drag_widget.hide()  # 初始化时隐藏组件

    def _get_drag_widget_palette(self):
        """定义拖拽组件的背景调色板"""
        p = QPalette()
        p.setColor(QPalette.Background, QColor(0, 200, 100))
        return p

    def set_drag_data_on_widget(self, row_data):
        """设置拖拽窗口的数据，避免重复创建组件"""
        if self.drag_widget.layout() is None:
            drag_layout = QHBoxLayout(self.drag_widget)
            drag_layout.setContentsMargins(10, 0, 0, 0)
            self.labels = []
            for col in range(len(self.drag_keys)):
                text_label = QLabel(self.drag_widget)
                self.labels.append(text_label)
                text_label.setFixedWidth(self.columnWidth(col))
                drag_layout.addWidget(text_label)
            drag_layout.addStretch()

        # 仅更新拖拽窗口的文本数据
        for col, key in enumerate(self.drag_keys):
            self.labels[col].setText(str(row_data[col]))

    def mouseMoveEvent(self, event) -> None:
        """处理拖拽时的移动事件"""
        if self.drag_row != -1:
            self.drag_widget.move(event.pos())  # 移动拖拽窗口
            self.drag_widget.show()  # 显示拖拽窗口
            row = self.indexAt(event.pos()).row()  # 获取鼠标位置的行
            self._highlight_row(row)  # 高亮当前行

    def _highlight_row(self, row):
        """高亮指定行，恢复其他行的默认背景色"""
        self.set_row_bg_color(row, HIGHLIGHT_COLOR)  # 高亮当前行
        self.set_row_bg_color(row + 1, DEFAULT_COLOR)  # 恢复下一行
        self.set_row_bg_color(row - 1, DEFAULT_COLOR)  # 恢复上一行

    def set_row_bg_color(self, row, color):
        """设置指定行的背景颜色"""
        if row < 0:
            return
        for col in range(self.columnCount()):
            item = self.item(row, col)
            if item:
                item.setBackground(QBrush(color))

    def mousePressEvent(self, event) -> None:
        """处理鼠标按下事件，开始拖拽"""
        row, col = self.get_row_col_from_event(event)
        if col == FILE_COLUMN_INDEX:
            cur_item = self.item(row, TARGET_COLUMN_INDEX)
            if cur_item:
                self.drag_row = row
                self.cur_key = (cur_item.data(Qt.UserRole)[1], cur_item.data(Qt.UserRole)[2])

                # 设置拖拽窗口的数据
                self.set_drag_data_on_widget(self.grouped_data[self.cur_key][self.current_indices[self.cur_key]])
        super().mousePressEvent(event)

    def get_row_col_from_event(self, event):
        """从事件中获取行和列"""
        return self.indexAt(event.pos()).row(), self.indexAt(event.pos()).column()

    def mouseReleaseEvent(self, event) -> None:
        """处理鼠标释放事件，完成拖拽并交换行"""
        row, col = self.get_row_col_from_event(event)
        self._clear_row_highlight(row)  # 清除高亮

        cur_item = self.item(row, TARGET_COLUMN_INDEX)
        print(cur_item)

        if cur_item and self.drag_row != -1:
            self.move_row(self.drag_row, row)  # 移动行数据
            self.update_table_row(row, self.cur_key)  # 更新表格数据
            if len(self.grouped_data[self.cur_key]) > 1:
                self._add_navigation_buttons(row, self.cur_key)
            self.selectRow(row)

            self.init_drag_widget()  # 重置拖拽组件
            self.drag_row = -1

        super().mouseReleaseEvent(event)

    def move_row(self, from_row, to_row):
        """将一行数据从一个位置移动到另一个位置"""
        if from_row == to_row:
            return
        self.removeRow(from_row)
        self.insertRow(to_row)

    def _clear_row_highlight(self, row):
        """清除行高亮，恢复为默认背景色"""
        self.set_row_bg_color(row, DEFAULT_COLOR)

    def _add_navigation_buttons(self, row, key):
        """为指定行添加导航按钮"""
        prev_button = QPushButton('<<')
        prev_button.clicked.connect(lambda _, k=key: self.navigate_data(k, self.currentRow(), 'previous'))
        self.setCellWidget(row, 0, prev_button)

        next_button = QPushButton('>>')
        next_button.clicked.connect(lambda _, k=key: self.navigate_data(k, self.currentRow(), 'next'))
        self.setCellWidget(row, 13, next_button)

    def set_data(self):
        """设置表格的初始数据"""
        self.setColumnCount(len(self.data_keys))
        self.setHorizontalHeaderLabels(self.data_keys)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)

        for row, key in enumerate(self.grouped_data.keys()):
            print(f"Setting row {row} with data: {key}")
            self.insertRow(row)
            self.update_table_row(row, key)
            if len(self.grouped_data[key]) > 1:
                self._add_navigation_buttons(row, key)

    def navigate_data(self, key, row, direction):
        """根据方向导航数据，支持前一条和后一条"""
        current_index = self.current_indices[key]
        if direction == 'previous':
            self.current_indices[key] = (current_index - 1) % len(self.grouped_data[key])
        else:
            self.current_indices[key] = (current_index + 1) % len(self.grouped_data[key])
        self.update_table_row(row, key)

    def update_table_row(self, row, key):
        """更新指定行的数据"""
        current_index = self.current_indices[key]
        current_data = self.grouped_data[key][current_index]
        print(f"Updating row {row} with data: {current_data}")  # 调试输出
        for col, value in enumerate(current_data):
            item = self.item(row, col + 1)
            if not item or item.text() != str(value):  # 只有在数据不同的时候才更新
                item = QTableWidgetItem(str(value))
                if col == FILE_COLUMN_INDEX:
                    item.setData(Qt.UserRole, current_data)
                self.setItem(row, col + 1, item)



