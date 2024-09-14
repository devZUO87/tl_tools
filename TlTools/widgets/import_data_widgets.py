from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog
from TlTools.data.data_oop import MeasurementData


class ImportDataWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window  # 传入主窗口实例
        self.import_button = None
        self.label = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('导入数据')
        self.setGeometry(400, 400, 300, 200)

        layout = QVBoxLayout()

        self.label = QLabel('请选择数据文件夹')
        layout.addWidget(self.label)

        self.import_button = QPushButton('导入数据')
        self.import_button.clicked.connect(self.import_data)
        layout.addWidget(self.import_button)

        self.setLayout(layout)

    def import_data(self):

        # 弹出文件夹选择对话框
        path = QFileDialog.getExistingDirectory(self, '选择文件夹')
        if path:
            self.main_window.showMaximized()
            self.main_window.status_bar.showMessage(f"已加载数据: {path}")
            # 调用主窗口的方法来创建并显示DraggableTableWidget
            example = MeasurementData(path)
            original_data = example.original_data
            self.main_window.set_table_widget(original_data)
            self.close()  # 关闭导入窗口