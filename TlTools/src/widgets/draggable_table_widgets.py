# _*_ coding:utf-8 _*_
# @File  : 拖拽表格.py
# @Time  : 2024/8/28
# @Author: zuo
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QPalette
from PyQt6.QtWidgets import (QTableWidget, QTableWidgetItem, QApplication,
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
        # self.data_keys = ["上一个", "气象改正(m)", "加乘常数改正(m)", "平距(m)", "高差(m)", "下一个"]
        # self.drag_keys = [ "气象改正(m)", "加乘常数改正(m)", "平距(m)", "高差(m)"]
        self.data_keys = ["上一个", "文件名", "测站", "目标", "归零方向均值", "天顶角均值", "斜距(m)", "仪器高(m)", "目标高(m)",
                          "测站温度(℃)", "目标温度(℃)", "测站气压(hPa)", "目标气压(hPa)", "气象改正(m)", "加乘常数改正(m)", "平距(m)", "高差(m)","高差中数(m)","往返不符值(mm)","限差(mm)","下一个"]
        self.drag_keys = ["文件名", "测站", "目标", "归零方向均值", "天顶角均值", "斜距(m)", "仪器高(m)", "目标高(m)",
                          "测站温度(℃)", "目标温度(℃)", "测站气压(hPa)", "目标气压(hPa)", "气象改正(m)", "加乘常数改正(m)", "平距(m)", "高差(m)","高差中数(m)","往返不符值(mm)","限差(mm)"]
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
        p.setColor(QPalette.ColorRole.Window, QColor(0, 200, 100))
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
            if col < len(row_data):
                print(row_data[col])
                self.labels[col].setText(str(row_data[col]))
            else:
                print(f"索引 {col} 超出范围，最大索引为 {len(row_data) - 1}")
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
        last_column_index = self.columnCount()
        prev_button = QPushButton('<<')
        prev_button.clicked.connect(lambda _, k=key: self.navigate_data(k, self.currentRow(), 'previous'))
        self.setCellWidget(row, 0, prev_button)

        next_button = QPushButton('>>')
        next_button.clicked.connect(lambda _, k=key: self.navigate_data(k, self.currentRow(), 'next'))
        self.setCellWidget(row, last_column_index-1, next_button)

    def set_data(self):
        """设置表格的初始数据"""
        self.setColumnCount(len(self.data_keys))
        self.setHorizontalHeaderLabels(self.data_keys)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)

        for row, key in enumerate(self.grouped_data.keys()):
            # print(f"Setting row {row} with data: {key}")
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
        # print(f"Updating row {row} with data: {current_data}")  # 调试输出
        for col, value in enumerate(current_data):
            item = self.item(row, col + 1)
            if not item or item.text() != str(value):  # 只有在数据不同的时候才更新
                item = QTableWidgetItem(str(value))
                if col == FILE_COLUMN_INDEX:
                    item.setData(Qt.UserRole, current_data)
                self.setItem(row, col + 1, item)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    data = {('JS02', 'KZ01'): [('JS02-0519', 'JS02', 'KZ01', '0.0', '84.39384', '454.43776875', 0.237, 1.318, 19.6, 19.6, 775, 775, 454.4708728301876, 454.46948846596666, 452.4975687624054, 41.223080948425434), ('JS02-0520', 'JS02', 'KZ01', '0.0', '84.37235', '454.4947916666667', 0.238, 1.619, 23, 23, 780, 780, 454.52839559896404, 454.52701109496275, 452.52708310991244, 41.22440344908071), ('JS02SS2-0520', 'JS02', 'KZ01', '0.0', '89.46164', '817.4432666666668', 0.238, 1.619, 23, 23, 780, 780, 817.5037058811389, 817.5014393471337, 817.4949224575488, 1.9283193047252942)], ('KZ01', 'JS02'): [('KZ01S-0519', 'KZ01', 'JS02', '359.58548', '95.22223', '454.47635625', 1.592, 0.249, 19.6, 19.6, 775, 775, 454.5094631411417, 454.50807868314627, 452.5111649620395, -41.201835312979846)], ('JS03', 'KZ03'): [('JS03-0519', 'JS03', 'KZ03', '0.0', '94.02205', '542.6668875', 0.234, 1.304, 22, 22, 775, 775, 542.707361268466, 542.7057624895781, 541.3578459741698, -39.27622200967495), ('JS03S-0520', 'JS03', 'KZ03', '0.0', '94.01076', '542.6499375', 0.234, 1.497, 26.6, 26.6, 784, 784, 542.6908604548578, 542.6892617160669, 541.3548621468085, -39.276731757767294)], ('KZ03', 'JS03'): [('KZ03SS-0519', 'KZ03', 'JS03', '0.0', '85.58538', '542.651375', 1.496, 0.241, 21.4, 21.4, 775, 775, 542.6916134203238, 542.6900146797033, 541.3558713952328, 39.3046700851178), ('KZ03SS-0519', 'KZ03', 'JS03', '269.5957', '85.58554', '542.6513500000001', 1.496, 0.241, 21.4, 21.4, 775, 775, 542.6915884184701, 542.6899896779103, 541.3561414371793, 39.300469044134516)], ('KZ01', 'KZ02'): [('KZ01-0519', 'KZ01', 'KZ02', '0.0', '89.59415', '1157.61235625', 1.592, 1.604, 25, 25, 775, 775, 1157.7011624553702, 1157.6980692415455, 1157.6980645850572, 0.18229348831654554), ('KZ01-0520', 'KZ01', 'KZ02', '0.0', '89.59451', '1157.6189125', 1.618, 1.604, 26.6, 26.6, 784, 784, 1157.7062122179675, 1157.7031189918719, 1157.7031159712978, 0.18808899951186236), ('KZ01S-0520', 'KZ01', 'KZ02', '0.0', '89.5929', '1157.616983333333', 1.523, 1.604, 18.2, 18.2, 782, 782, 1157.6978802277338, 1157.6947870218848, 1157.6947739470202, 0.1834509630889752)], ('KZ02', 'KZ01'): [('KZ02S-0519', 'KZ02', 'KZ01', '0.0', '90.0124', '1157.61195625', 1.579, 1.318, 21, 21, 775, 775, 1157.6974607407117, 1157.694367535882, 1157.694271535663, -0.12000514289638556), ('KZ02-0520', 'KZ02', 'KZ01', '0.0', '90.00212', '1157.61936875', 1.521, 1.604, 14.6, 14.6, 781, 781, 1157.6974541751536, 1157.6943609703399, 1157.694354855496, -0.11153005136692437), ('KZ02S-0520', 'KZ02', 'KZ01', '0.0', '90.00211', '1157.61865', 1.521, 1.604, 14.6, 14.6, 781, 781, 1157.6967353766713, 1157.6936421736043, 1157.6936361163152, -0.11096882409492521)], ('KZ01', 'KZ03'): [('KZ01S-0519', 'KZ01', 'KZ03', '0.0', '94.2523', '608.4656625', 1.592, 1.304, 19.6, 19.6, 775, 775, 608.5099869322281, 608.50822825296, 606.6959691235021, -46.61545236705874)], ('KZ03', 'KZ01'): [('KZ03S-0519', 'KZ03', 'KZ01', '0.0', '85.37179', '608.42435', 1.496, 1.318, 19.6, 19.6, 775, 775, 608.468671422768, 608.4669128438965, 606.691196826227, 46.65470709476497), ('KZ03S-0520', 'KZ03', 'KZ01', '0.0', '85.35392', '608.4769291666667', 1.488, 1.619, 24, 24, 780, 780, 608.52235324099, 608.5205945316717, 606.7224226951757, 46.64013660108855)], ('KZ02', 'KZ03'): [('KZ02-0519', 'KZ02', 'KZ03', '0.0', '94.32273', '594.46360625', 1.579, 1.304, 21, 21, 775, 775, 594.5075150120203, 594.5057903587589, 592.6396661081056, -46.76891564764481), ('KZ02S1-0520', 'KZ02', 'KZ03', '0.0', '94.30519', '594.438', 1.502, 1.497, 26.6, 26.6, 784, 784, 594.4828284570931, 594.48110386382, 592.6367621639982, -46.76286467653299)], ('KZ03', 'KZ02'): [('KZ03-0519', 'KZ03', 'KZ02', '0.0', '85.2836', '594.43970625', 1.496, 1.604, 21.4, 21.4, 775, 775, 594.4837848534261, 594.482060257829, 592.6304264555797, 46.79957802741251), ('KZ03-0520', 'KZ03', 'KZ02', '0.0', '85.28345', '594.4427708333334', 1.488, 1.604, 21.4, 21.4, 784, 784, 594.4853848427134, 594.4836602432283, 592.6316804917643, 46.79601405114258)], ('JS02', 'KZ02'): [('JS02S-0520', 'JS02', 'KZ02', '0.0', '86.39069', '731.0709', 0.238, 1.604, 24, 24, 780, 780, 731.1254759704361, 731.1234193355295, 729.8755061635425, 41.3688987490301), ('JS02SS-0520', 'JS02', 'KZ02', '0.0', '86.3906', '731.0705791666668', 0.238, 1.604, 24, 24, 780, 780, 731.125155113152, 731.1230984790251, 729.8749995385344, 41.372064641383524)], ('KZ02', 'JS02'): [('KZ02SS-0520', 'KZ02', 'JS02', '0.0', '93.20394', '731.0725708333333', 1.502, 0.243, 25, 25, 784, 784, 731.1268752976346, 731.1248186593276, 729.8797375357991, -41.35559206385429), ('KZ02SS1-0520', 'KZ02', 'JS02', '0.0', '93.20349', '731.0706291666667', 1.502, 0.243, 24, 24, 780, 780, 731.1252051168844, 731.123148482636, 729.8790005181388, -41.339571226362644)], ('JS03', 'JS02'): [('JS03-0520', 'JS03', 'JS02', '0.0', '92.52502', '676.3338916666667', 0.234, 0.126, 23, 23, 780, 780, 676.3838976925281, 676.3819740796567, 675.5273117833381, -33.852756512674354)]}

    table_widget = DraggableTableWidget(data)
    table_widget.show()
    sys.exit(app.exec_())