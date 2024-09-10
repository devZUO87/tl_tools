import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QStatusBar

from TlTools.widgets.draggable_table_widgets import DraggableTableWidget
from TlTools.widgets.file_menu import FileMenu
from TlTools.widgets.import_data_widgets import ImportDataWindow
from TlTools.widgets.matching_measure_widgets import MatchingMeasureWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("三角高程计算工具")
        self.setGeometry(100, 100, 1200, 800)

        # 创建中心部件和布局
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 添加导入数据窗口
        self.import_data_window = ImportDataWindow(self)
        self.import_data_window.show()

        # 表格部件占位符
        self.drag_table_widget = None
        self.drag_table_widget_data = None

        # 创建菜单栏
        self.menu_bar_component = FileMenu(self)
        self.setMenuBar(self.menu_bar_component.menu_component)

        # 创建匹配测量部件
        self.matching_measure_widget = MatchingMeasureWidget(self)

    def set_table_widget(self, path):
        self.show()
        # 如果已有表格，则先关闭
        if self.drag_table_widget:
            self.drag_table_widget.deleteLater()

        # 创建新的表格并添加到布局中
        self.drag_table_widget = DraggableTableWidget(path)
        self.layout.addWidget(self.drag_table_widget)

        # 更新状态栏
        self.status_bar.showMessage(f"已加载数据: {path}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()

    sys.exit(app.exec_())
