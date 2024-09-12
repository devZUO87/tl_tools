import sys

import openpyxl
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QStatusBar, QMessageBox, QFileDialog, \
    QTableWidgetItem, QTableWidget, QHeaderView
from openpyxl.workbook import Workbook

from TlTools.data.data_oop import MeasurementData
from TlTools.widgets.import_data_widgets import ImportDataWindow
from TlTools.widgets.matching_measure_widgets import MatchingMeasureWidget
from TlTools.widgets.menu_component import MenuComponent


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("三角高程计算工具")



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

        # # 表格部件占位符
        # self.drag_table_widget = None
        # self.drag_table_widget_data = None

        # Create a table widget
        self.table_widget = QTableWidget()
        self.data_keys = ["文件名", "测站", "目标", "归零方向均值", "天顶角均值", "斜距" ,"仪器高(m)", "目标高(m)", "测站温度", "目标温度", "测站气压", "目标气压"]
        self.table_widget.setColumnCount(len(self.data_keys))
        self.table_widget.setHorizontalHeaderLabels(self.data_keys)
        self.layout.addWidget(self.table_widget)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)



        # 创建匹配测量部件
        self.matching_measure_widget = MatchingMeasureWidget(self)

    def initMenu(self):
        file_menu = self.menu_component.add_menu('文件')
        self.menu_component.add_action(file_menu, '打开', '打开文件夹', self.openFile)
        self.menu_component.add_action(file_menu, '退出', '退出程序', self.close)

        import_menu = self.menu_component.add_menu('导入')
        self.menu_component.add_action(import_menu, '导入外业手簿', '导入', self.showAbout)

        export_menu = self.menu_component.add_menu('导出')
        self.menu_component.add_action(export_menu, '导出匹配表', '导出匹配表', self.exportMatchingTable)
        self.menu_component.add_action(export_menu, '导出外业测量数据', '导出外业测量数据', self.showAbout)
        self.menu_component.add_action(export_menu, '导出三角高程测量计算总表', '导出三角高程测量计算总表', self.showAbout)

        help_menu = self.menu_component.add_menu('帮助')
        self.menu_component.add_action(help_menu, '关于', '关于程序', self.showAbout)

    def openFile(self):
        try:
            self.close()
            self.import_data_window.show()
            self.import_data_window.label.setText('请选择数据文件夹')
        except AttributeError:
            QMessageBox.warning(self, '错误', '没有可导入的数据')


    def showAbout(self):
        QMessageBox.about(self, '关于', '这是一个三角高程测量程序')

    def set_table_widget(self, path):
        # 加载数据并显示表格
        self.showMaximized()
        example = MeasurementData(path)
        original_data = example.original_data
        print(original_data)

        self.table_widget.setRowCount(len(original_data))
        self.table_widget.setColumnCount(len(self.data_keys))

        for row_idx, row_data in enumerate(original_data):
            for col_idx in range(len(self.data_keys)):
                if col_idx < len(row_data):
                    cell_data = row_data[col_idx]
                else:
                    cell_data = ''  # 如果数据列数不足，填充空字符串
                self.table_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(cell_data)))
        # 更新状态栏
        self.status_bar.showMessage(f"已加载数据: {path}")


    def exportMatchingTable(self):
        # 导出匹配表
        if self.drag_table_widget:
            try:
                data = self.drag_table_widget.all_table_data
                wb = Workbook()
                ws = wb.active
                ws.append(
                    ["文件名", "测站", "目标", "归零方向均值", "天顶角均值", "斜距", "仪器高(m)", "目标高(m)", "测站温度",
                     "目标温度", "测站气压", "目标气压"])
                # 写入数据
                for row in data:
                    # 处理 None 值，避免写入到 Excel
                    clean_row = [cell if cell is not None else '' for cell in row]
                    ws.append(clean_row)
                # 表格格式
                for row in ws.iter_rows(min_row=1):
                    for cell in row:
                        cell.alignment = openpyxl.styles.Alignment(horizontal='center', vertical='center')
                # 宽度
                # 定义字典来存储各列的宽度
                column_widths = {'A': 20, 'B': 10, 'C': 10, 'D': 16, 'E': 20, 'F': 10, 'G': 10, 'H': 10, 'I': 10}

                # 使用循环设置列宽
                for col, width in column_widths.items():
                    ws.column_dimensions[col].width = width

                # 保存为 Excel 文件
                file_path, _ = QFileDialog.getSaveFileName(self, '选择文件夹和输入文件名', '', 'Excel Files (*.xlsx)')

                if file_path:
                    # 保存文件
                    wb.save(file_path)
                    QMessageBox.warning(self, '完成', f'文件已保存到: {file_path}')
            except Exception as e:
                QMessageBox.warning(self, '错误', e)
        else:
            QMessageBox.warning(self, '错误', '没有可导出的数据')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())
