import sys
import os
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from src.auth.auth import AuthManager
from src.widgets.register_dialog import RegisterDialog
from src.widgets.main_window import MainWindow  # 从主窗口模块导入你的窗口
from src.function.logger import log_operation, log_error, performance_monitor


# def main():
    # app = QApplication(sys.argv)
    # main_window = MainWindow()
    # sys.exit(app.exec_())

@performance_monitor
def main():
    try:
        log_operation("正在初始化应用程序...", "INFO")
        print("正在初始化应用程序...")
        app = QApplication(sys.argv)
        
        # 检查程序是否可以正常创建文件
        try:
            test_file_path = "test_write.tmp"
            with open(test_file_path, "w") as f:
                f.write("测试写入权限")
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
                log_operation("文件写入测试成功", "INFO")
                print("文件写入测试成功")
            else:
                log_operation("警告：无法确认文件写入", "WARNING")
                print("警告：无法确认文件写入")
        except Exception as e:
            error_msg = f"警告：文件写入测试失败 - {e}"
            log_operation(error_msg, "WARNING")
            print(error_msg)
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("警告")
            msg_box.setText(f"程序可能没有足够的权限写入文件。\n{str(e)}\n\n请以管理员身份运行程序。")
            msg_box.exec()
        
        log_operation("正在检查注册状态...", "INFO")
        print("正在检查注册状态...")
        auth_manager = AuthManager()
        if not auth_manager.is_registered():
            log_operation("未注册，显示注册对话框...", "INFO")
            print("未注册，显示注册对话框...")
            dialog = RegisterDialog()
            if dialog.exec() != RegisterDialog.DialogCode.Accepted:
                log_operation("用户取消注册，程序退出", "INFO")
                print("用户取消注册，程序退出")
                return 1
        
        log_operation("已注册，启动主程序...", "INFO")
        print("已注册，启动主程序...")
        main_window = MainWindow()
        main_window.show() 
        sys.exit(app.exec())
        # controller = Controller()
        # return controller.run()
    except Exception as e:
        error_msg = f"发生错误: {str(e)}"
        log_error(e, "程序启动失败")
        print(error_msg)
        print("错误详情:")
        traceback.print_exc()
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("错误")
        msg_box.setText(f"程序启动失败：{str(e)}")
        msg_box.exec()
        return 1

if __name__ == "__main__":
    main()
