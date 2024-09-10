from PyQt5.QtWidgets import QWidget, QMessageBox

from TlTools.widgets.menu_component import MenuComponent


class FileMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.main_window = parent  # 传入主窗口实例
        self.menu_component = MenuComponent(self.main_window)
        self.initMenu()

    def initMenu(self):
        file_menu = self.menu_component.add_menu('文件')
        self.menu_component.add_action(file_menu, '打开', '打开文件夹', self.openFile)
        self.menu_component.add_action(file_menu, '导入', '导入数据', self.importData)
        self.menu_component.add_action(file_menu, '退出', '退出程序', self.main_window.close)

        help_menu = self.menu_component.add_menu('帮助')
        self.menu_component.add_action(help_menu, '关于', '关于程序', self.showAbout)

    def openFile(self):
        self.main_window.close()

        self.main_window.import_data_window.show()
        self.main_window.import_data_window.label.setText('请选择数据文件夹')


    def importData(self):
        # 这里可以获取数据并显示
        # QMessageBox.information(self.main_window, '提示', '导入数据')
        self.main_window.drag_table_widget_data = self.main_window.drag_table_widget.get_all_table_data()

        # 调用匹配测量窗口来显示导入的数据
        self.main_window.matching_measure_widget.show()
        self.main_window.matching_measure_widget.showData()

    def showAbout(self):
        QMessageBox.about(self.main_window, '关于', '这是一个三角高程测量程序')
