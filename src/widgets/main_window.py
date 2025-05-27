import math
import sys
from collections import defaultdict

import openpyxl
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QStatusBar,
    QMessageBox,
    QFileDialog,
    QTableWidgetItem,
    QTableWidget,
    QHeaderView,
)
from PyQt6.QtGui import QPalette, QColor
from src.widgets.draggable_table_widgets import DraggableTableWidget
from src.widgets.import_data_widgets import ImportDataWindow
from src.widgets.menu_component import MenuComponent
from src.widgets.parameter_window import ParameterWindow
from src.data.data_service import DataService


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.matched = None # 匹配状态
        self.calculated = None  # 计算状态
        self.setWindowTitle("三角高程计算工具")
        self.init_ui()
        self.setup_styles()
        self.resize(800, 600)
           # 将窗口移动到屏幕中心
        screen = QApplication.primaryScreen().geometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)
        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 创建菜单栏
        self.menu_component = MenuComponent(self)
        self.setMenuBar(self.menu_component)  # 使用 setMenuBar 设置菜单
        self.initFileMenu()

        # 创建中心部件和布局
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # 添加导入数据窗口
        self.grouped_data = defaultdict(list)
        self.import_data_window = ImportDataWindow(self)
        # self.import_data_window.show()

        # Create a table widget
        self.table_widget = QTableWidget()
        self.data_keys = ["文件名", "测站", "目标", "归零方向均值", "天顶角均值", "斜距", "仪器高(m)", "目标高(m)",
                          "测站温度", "目标温度", "测站气压", "目标气压"]
        self.table_widget.setColumnCount(len(self.data_keys))
        self.table_widget.setHorizontalHeaderLabels(self.data_keys)
        self.layout.addWidget(self.table_widget)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.data = []
        self.data_service = DataService()


    def setup_styles(self):
            """设置全局样式"""
            self.setAutoFillBackground(True)
            palette = self.palette()
            palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))  # 浅灰色背景
            palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))    # 黑色文字
            palette.setColor(QPalette.ColorRole.Button, QColor(225, 225, 225))  # 按钮颜色
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))    # 按钮文字颜色
            self.setPalette(palette)

    def init_ui(self):
        # 现代化QSS样式
        self.setStyleSheet("""
        QWidget {
            background: #FFFFFF;
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            color: #222;
        }
        QGroupBox {
            border: 1px solid #E5E5E5;
            border-radius: 10px;
            margin-top: 16px;
            background: #fff;
        }
        QGroupBox:title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 6px 0 6px;
            font-weight: bold;
            color: #0078D4;
            font-size: 11pt;
        }
        QPushButton {
            background-color: #0078D4;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 28px;
            font-size: 11pt;
            font-weight: 600;
        }
        QPushButton:hover {
            background-color: #005A9E;
        }
        QLineEdit, QComboBox {
            border: 1px solid #BDBDBD;
            border-radius: 8px;
            padding: 6px 10px;
            background: #fff;
            font-size: 10.5pt;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 28px;
            border: none;
            border-top-right-radius: 8px;
            border-bottom-right-radius: 8px;
            border-top-left-radius: 0px;
            border-bottom-left-radius: 0px;
            background: #E3F2FD;
            margin: 1px 1px 1px 0;
        }
        QComboBox QAbstractItemView {
            border: 1px solid #BDBDBD;
            background: #fff;
            selection-background-color: #E3F2FD;
            selection-color: #0078D4;
            border-radius: 8px;
            padding: 4px;
            margin: 0px;
            outline: none;        
        }
        QComboBox::view {
            margin: 0;
            padding: 0;
            border-radius: 8px;
            background: transparent;
        }               
        QLabel {
            font-size: 10.5pt;
        }
        QProgressBar {
            border: 1px solid #BDBDBD;
            border-radius: 8px;
            text-align: center;
            background: #E3F2FD;
            height: 18px;
        }
        QProgressBar::chunk {
            background-color: #0078D4;
            border-radius: 8px;
        }
        QCheckBox {
            spacing: 8px;
            font-size: 10pt;
        }
        """)

    def initFileMenu(self):
        file_menu = self.menu_component.add_menu('文件')
        self.menu_component.add_action(file_menu, '打开', '打开文件夹', self.openFile)
        self.menu_component.add_action(file_menu, '退出', '退出程序', self.close)

        import_menu = self.menu_component.add_menu('导入')
        self.menu_component.add_action(import_menu, '导入外业手簿', '导入', self.importMatchingTable)


        export_menu = self.menu_component.add_menu('导出')
        self.menu_component.add_action(export_menu, '导出外业测量数据', '导出外业测量数据', self.exportOutsideTable)
        self.menu_component.add_action(export_menu, '导出三角高程测量计算总表', '导出三角高程测量计算总表',
                                       self.exportOutsideTable)

        measure_menu = self.menu_component.add_menu('处理')
        self.menu_component.add_action(measure_menu, '匹配外业手簿', '匹配', self.set_draggable_table_widget)
        self.menu_component.add_action(measure_menu, '计算对象观测中误差', '对象观测计算', self.calculate_draggable_table_widget)

        measure_menu = self.menu_component.add_menu('设置')
        self.menu_component.add_action(measure_menu, '参数设置', '参数设置', self.set_parameter)

        help_menu = self.menu_component.add_menu('帮助')
        self.menu_component.add_action(help_menu, '关于', '关于程序', self.showAbout)

    def openFile(self):
        try:
            self.matched = False
            self.close()
            self.import_data_window.show()
            self.import_data_window.label.setText('请选择数据文件夹')
        except AttributeError:
            QMessageBox.warning(self, '错误', '没有可导入的数据')

    def importMatchingTable(self):
        try:
            file_dialog_result = QFileDialog.getOpenFileName(self, '选择文件', '', 'Excel Files (*.xlsx)')
            file_path = file_dialog_result[0]
            if file_path:
                data = self.data_service.import_excel(file_path)
                self.data = data
                self.set_table_widget(data)
            else:
                QMessageBox.warning(self, '错误', '没有选择文件')
        except AttributeError:
            QMessageBox.warning(self, '错误', '没有可导入的数据')

    def set_table_widget(self, data):
        # 清空现有表格内容
        self.table_widget.clear()

        # 设置行数
        self.table_widget.setRowCount(len(data))

        # 设置列数
        self.table_widget.setColumnCount(len(self.data_keys))

        # 重新设置表头
        self.table_widget.setHorizontalHeaderLabels(self.data_keys)

        # 设置表格数据
        for row_idx, row_data in enumerate(data):
            for col_idx, cell_data in enumerate(row_data):
                self.table_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(cell_data)))

    def exportOutsideTable(self):
        # 导出匹配表
        if self.table_widget:
            try:
                data = self.get_all_table_data()
                file_dialog_result = QFileDialog.getSaveFileName(self, '选择文件夹和输入文件名', '', 'Excel Files (*.xlsx)')
                file_path = file_dialog_result[0]
                if file_path:
                    self.data_service.export_excel(data, file_path, calculated=self.calculated)
                    QMessageBox.warning(self, '完成', f'文件已保存到: {file_path}')
            except Exception as e:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.setWindowTitle("警告")
                msg_box.setText(f"程序可能没有足够的权限写入文件。\n{str(e)}\n\n请以管理员身份运行程序。")
                msg_box.exec()
        else:
            QMessageBox.warning(self, '错误', '没有可导出的数据')

    def get_all_table_data(self):
        data = []
        for row in range(self.table_widget.rowCount()):
            if self.matched:
                row_data = [self.table_widget.item(row, col).text() if self.table_widget.item(row, col) else None for col in range(self.table_widget.columnCount())[1:-1]]
            else:
                row_data = [self.table_widget.item(row, col).text() if self.table_widget.item(row, col) else None for col in range(self.table_widget.columnCount())]
            data.append(row_data)
        return data

    def set_draggable_table_widget(self):
        if self.matched:
            QMessageBox.warning(self, '错误', '已匹配，无法重复匹配')
        else:
            self.grouped_data = self.data_service.group_data(self.data)
            self.matched = True
            self.grouped_data = self.data_service.sort_and_calculate(self.grouped_data)
            self.table_widget.clear()

            self.table_widget = DraggableTableWidget(self.grouped_data,self)
            central_widget = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(self.table_widget)
            central_widget.setLayout(layout)

            # 将 central_widget 作为主窗口的中央组件
            self.setCentralWidget(central_widget)
            self.calculated = True
            self.calculate_draggable_table_widget()

    def calculate_draggable_table_widget(self):
        '''
        计算对象观测中误差
        1. 获取当前行和下一行的第六列和第十四列数据
        2. 计算平均值、和与容差
        3. 将结果追加到当前行的指定列
        4. 更新表格
        '''
        if self.matched:
            for i in range(0, self.table_widget.rowCount(), 2):  # 每两行遍历
                if i + 1 >= self.table_widget.rowCount():  # 确保有下一行
                    continue

                # 获取当前行和下一行的第六列和第十四列数据
                def get_row_value(row, col):
                    item = self.table_widget.item(row, col)
                    return float(item.text()) if item else 0

                first_row_value = get_row_value(i, 16)
                second_row_value = get_row_value(i + 1, 16)
                first_row_value_1 = get_row_value(i, 6)
                second_row_value_1 = get_row_value(i + 1, 6)

                # 计算平均值、和与容差
                average_d =round( 0.5 * (first_row_value - second_row_value),5)
                sum_value = round((first_row_value + second_row_value) * 1000,5)
                tolerance = round(40 * math.sqrt(0.5 * (abs(first_row_value_1) + abs(second_row_value_1)) / 1000),5)

                # 将结果追加到当前行的指定列
                self.table_widget.setItem(i, self.table_widget.columnCount() - 4, QTableWidgetItem(str(average_d)))
                self.table_widget.setItem(i, self.table_widget.columnCount() - 3, QTableWidgetItem(str(sum_value)))
                self.table_widget.setItem(i, self.table_widget.columnCount() - 2, QTableWidgetItem(str(tolerance)))


        else:
            QMessageBox.warning(self, '错误', "没有可计算的数据")
            # 可以在这里显示结果，例如通过弹窗或更新表格

    def showAbout(self):
        QMessageBox.about(self, "关于", "这是一个程序")
    
    def set_parameter(self):
        parameter_window = ParameterWindow(self)
        parameter_window.exec()
    # 使用函数处理数据



if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        main_window = MainWindow()
        sys.exit(app.exec_())
    except Exception as e:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("错误")
        msg_box.setText(f"程序启动失败：{str(e)}")
        msg_box.exec()
