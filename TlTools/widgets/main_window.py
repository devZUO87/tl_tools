import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QStatusBar, QMessageBox

from TlTools.widgets.draggable_table_widgets import DraggableTableWidget
from TlTools.widgets.import_data_widgets import ImportDataWindow
from TlTools.widgets.matching_measure_widgets import MatchingMeasureWidget
from TlTools.widgets.menu_component import MenuComponent


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("三角高程计算工具")
        self.setGeometry(100, 100, 1200, 800)

        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 创建菜单栏
        self.menu_component = MenuComponent(self)
        self.setMenuBar(self.menu_component)  # 使用 setMenuBar 设置菜单
        self.initMenu()

        # 创建中心部件和布局
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # 添加导入数据窗口
        self.import_data_window = ImportDataWindow(self)
        self.import_data_window.show()

        # 表格部件占位符
        self.drag_table_widget = None
        self.drag_table_widget_data = None

        # 创建匹配测量部件
        self.matching_measure_widget = MatchingMeasureWidget(self)

    def initMenu(self):
        file_menu = self.menu_component.add_menu('文件')
        self.menu_component.add_action(file_menu, '打开', '打开文件夹', self.openFile)
        self.menu_component.add_action(file_menu, '导入', '导入数据', self.importData)
        self.menu_component.add_action(file_menu, '退出', '退出程序', self.close)

        help_menu = self.menu_component.add_menu('帮助')
        self.menu_component.add_action(help_menu, '关于', '关于程序', self.showAbout)

    def openFile(self):
        self.import_data_window.show()
        self.import_data_window.label.setText('请选择数据文件夹')

    def importData(self):
        # 这里可以获取数据并显示
        try:
            self.drag_table_widget_data = self.drag_table_widget.get_all_table_data()
            self.matching_measure_widget.show()
        except AttributeError:
            QMessageBox.warning(self, '错误', '没有可导入的数据')

    def showAbout(self):
        QMessageBox.about(self, '关于', '这是一个三角高程测量程序')

    def set_table_widget(self, path):
        self.show()
        # 如果已有表格，则先关闭并移除
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
    main_window.show()
    sys.exit(app.exec_())
