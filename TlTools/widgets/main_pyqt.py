# _*_ coding:utf-8 _*_
# @File  : 拖拽表格.py
# @Time  : 2024/8/28
# @Author: zuo
import sys

from PyQt5.QtWidgets import (QApplication)

from TlTools.widgets.import_data_widgets import ImportDataWindow

if __name__ == '__main__':
    app = QApplication([])
    # 创建导入数据的界面
    window = ImportDataWindow()
    window.show()

    sys.exit(app.exec_())
