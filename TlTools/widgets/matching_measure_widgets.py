from PyQt5.QtWidgets import QWidget, QApplication
from TlTools.widgets.menu_component import MenuComponent

class MatchingMeasureWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window  # 传入主窗口实例
        self.import_button = None
        self.label = None
        self.menu_component = MenuComponent(self)
        self.initUI()


    def initUI(self):
        self.setWindowTitle('导入外业手簿')
        self.setGeometry(400, 400, 300, 200)

        data_menu = self.menu_component.add_menu('数据')
        self.menu_component.add_action(data_menu, '导出匹配表', '导出匹配表', self.exportData)
        self.menu_component.add_action(data_menu, '导入外业手簿', '导入外业手簿', self.importData)




    def exportData(self):
        print('导出匹配表')

    def importData(self):
        print('导入外业手簿')


    def showData(self):
        print(self.main_window.drag_table_widget_data)



