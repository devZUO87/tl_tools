# _*_ coding:utf-8 _*_
# @File  : 拖拽表格.py
# @Time  : 2024/8/28
# @Author: zuo
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QPalette
from PyQt5.QtWidgets import (QApplication, QTableWidget, QTableWidgetItem,
                             QAbstractItemView, QHeaderView, QWidget,
                             QPushButton, QLabel, QHBoxLayout)

from TlTools.data.data_oop import MeasurementData


class DraggableTableWidget(QTableWidget):
    def __init__(self, path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize(1000, 600)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.data_keys = ["上一个", "文件名", "测站", "目标", "归零方向均值", "天顶角均值", "斜距", "下一个"]
        self.drag_keys = ["文件名", "测站", "目标", "归零方向均值", "天顶角均值", "斜距"]
        self.setHorizontalHeaderLabels(self.data_keys)  # 设置表头
        self.path = path
        self.grouped_data = MeasurementData(path).grouped_data
        self.all_table_data = MeasurementData(path).original_data
        self.current_indices = {key: 0 for key in self.grouped_data}
        self.cur_key = None
        self.drag_row = -1
        self.drag_widget = None
        self.init_drag_widget()
        self.set_data()

    def init_drag_widget(self):
        if self.drag_widget:
            self.drag_widget.deleteLater()
        self.drag_widget = QWidget(self)
        self.drag_widget.setAutoFillBackground(True)
        self.drag_widget.setPalette(self._get_drag_widget_palette())
        self.drag_widget.resize(self.width(), 30)
        self.drag_widget.hide()

    def _get_drag_widget_palette(self):
        p = QPalette()
        p.setColor(QPalette.Background, QColor(0, 200, 100))
        return p

    def set_drag_data_on_widget(self, row_data):
        drag_layout = QHBoxLayout(self.drag_widget)
        drag_layout.setContentsMargins(10, 0, 0, 0)
        for col, key in enumerate(self.drag_keys):
            text_label = QLabel(str(row_data[col]), self.drag_widget)
            text_label.setFixedWidth(self.columnWidth(col))
            drag_layout.addWidget(text_label)
            button = QPushButton(self)
            button.setFocusPolicy(Qt.NoFocus)
            button.setFixedWidth(1)
            drag_layout.addWidget(button)
        drag_layout.addStretch()

    def mouseMoveEvent(self, event) -> None:
        if self.drag_row != -1:
            self.drag_widget.move(event.pos()) # 移动拖拽窗口
            self.drag_widget.show() # 显示拖拽窗口
            row = self.indexAt(event.pos()).row() # 获取鼠标位置的行
            self._highlight_row(row) # 高亮当前行

    def _highlight_row(self, row):
        self.set_row_bg_color(row, QColor(254, 163, 86))
        self.set_row_bg_color(row + 1, QColor(255, 255, 255))
        self.set_row_bg_color(row - 1, QColor(255, 255, 255))

    def set_row_bg_color(self, row, color):
        if row < 0:
            return
        for col in range(self.columnCount()):
            item = self.item(row, col)
            if item:
                item.setBackground(QBrush(color))

    def mousePressEvent(self, event) -> None:
        row, col = self.indexAt(event.pos()).row(), self.indexAt(event.pos()).column()
        if col == 1:

            cur_item = self.item(row, col+1)
            if cur_item:
                self.drag_row = row
                self.cur_key = (cur_item.data(Qt.UserRole)[1], cur_item.data(Qt.UserRole)[2])
                # print(self.grouped_data[self.cur_key][self.current_indices[self.cur_key]])

                self.set_drag_data_on_widget(self.grouped_data[self.cur_key][self.current_indices[self.cur_key]])
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        row, col = self.indexAt(event.pos()).row(), self.indexAt(event.pos()).column()
        self._clear_row_highlight(row)
        cur_item = self.item(row, 2)
        if cur_item and self.drag_row != -1:
            self.removeRow(self.drag_row)
            self.insertRow(row)
            self.update_table_row(row, self.cur_key)

            if len(self.grouped_data[self.cur_key]) > 1:
             self._add_navigation_buttons(row, self.cur_key)
            self.selectRow(row)

        self.init_drag_widget()
        self.drag_row = -1
        super().mouseReleaseEvent(event)

    def _clear_row_highlight(self, row):
        self.set_row_bg_color(row, QColor(255, 255, 255))

    def _add_navigation_buttons(self, row, key):
        prev_button = QPushButton('<<')
        prev_button.clicked.connect(lambda _, k=key: self.show_previous(k, self.currentRow()))
        self.setCellWidget(row, 0, prev_button)
        next_button = QPushButton('>>')
        next_button.clicked.connect(lambda _, k=key: self.show_previous(k, self.currentRow()))
        self.setCellWidget(row, 7, next_button)

    def set_data(self):
        self.setColumnCount(len(self.data_keys))
        self.setHorizontalHeaderLabels(self.data_keys)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        for row, key in enumerate(self.grouped_data.keys()):
            self.insertRow(row)
            self.update_table_row(row, key)
            if len(self.grouped_data[key]) > 1:
                self._add_navigation_buttons(row, key)

    def show_previous(self, key, row):
        current_index = self.current_indices[key]
        self.current_indices[key] = (current_index - 1) % len(self.grouped_data[key])
        self.update_table_row(row, key)

    def show_next(self, key, row):
        current_index = self.current_indices[key]
        self.current_indices[key] = (current_index + 1) % len(self.grouped_data[key])
        self.update_table_row(row, key)

    def update_table_row(self, row, key):
        current_index = self.current_indices[key]
        current_data = self.grouped_data[key][current_index]
        for col, value in enumerate(current_data):
            item = QTableWidgetItem(str(value))
            if col == 1:
                item.setData(Qt.UserRole, current_data)
            self.setItem(row, col + 1, item)

    def get_all_table_data(self):
        data = []
        for row in range(self.rowCount()):
            row_data = [self.item(row, col).text() if self.item(row, col) else None for col in range(self.columnCount())]
            data.append(row_data)
        return data


if __name__ == '__main__':
    app = QApplication([])

    # 创建导入数据的界面
    path = '/数据/原始数据/jc'
    window = DraggableTableWidget(path)
    window.show()

    sys.exit(app.exec_())
