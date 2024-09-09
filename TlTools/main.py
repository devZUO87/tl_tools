import sys
from PyQt5.QtWidgets import QApplication
from .widgets.main_pyqt import ImportDataWindow  # 从主窗口模块导入你的窗口


def main():
    app = QApplication([])
    # 创建导入数据的界面
    window = ImportDataWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
