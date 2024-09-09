from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog

from TlTools.widgets.draggable_table_widgets import DraggableTableWidget


class ImportDataWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.table_widget = None
        self.import_button = None
        self.label = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('导入数据')
        self.setGeometry(100, 100, 300, 200)

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
            self.label.setText(f'已选择: {path}')
            self.table_widget = DraggableTableWidget(path)
            self.table_widget.show()
            self.close()