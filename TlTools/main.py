import sys

from PyQt5.QtWidgets import QApplication

from TlTools.widgets.main_window import MainWindow  # 从主窗口模块导入你的窗口


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
