from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QMessageBox, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.auth.auth import AuthManager

class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth_manager = AuthManager()
        self.machine_code = self.auth_manager.get_machine_code()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("软件注册")
        self.setFixedWidth(500)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 机器码显示
        machine_code_layout = QVBoxLayout()
        machine_code_label = QLabel("您的机器码：")
        machine_code_label.setFont(QFont('Microsoft YaHei', 10))
        self.machine_code_edit = QLineEdit()
        self.machine_code_edit.setReadOnly(True)
        self.machine_code_edit.setText(self.machine_code)
        self.machine_code_edit.setFont(QFont('Consolas', 11))
        machine_code_layout.addWidget(machine_code_label)
        machine_code_layout.addWidget(self.machine_code_edit)
        layout.addLayout(machine_code_layout)
        
        # 注册码输入
        register_code_layout = QVBoxLayout()
        register_code_label = QLabel("请输入注册码：")
        register_code_label.setFont(QFont('Microsoft YaHei', 10))
        self.register_code_edit = QLineEdit()
        self.register_code_edit.setFont(QFont('Consolas', 11))
        register_code_layout.addWidget(register_code_label)
        register_code_layout.addWidget(self.register_code_edit)
        layout.addLayout(register_code_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.register_btn = QPushButton("注册")
        self.register_btn.setFont(QFont('Microsoft YaHei', 10))
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 4px;
                padding: 5px 15px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setFont(QFont('Microsoft YaHei', 10))
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF5252;
                color: white;
                border-radius: 4px;
                border: none;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        button_layout.addWidget(self.register_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #cccccc; margin-top: 10px;")
        layout.addWidget(separator)
        
        # 添加联系方式信息
        info_layout = QVBoxLayout()
        
        get_code_label = QLabel("获取注册码请联系:")
        get_code_label.setFont(QFont('Microsoft YaHei', 10, QFont.Weight.Bold))
        info_layout.addWidget(get_code_label)
        
        contact_label = QLabel("微信/电话: 18935590710")
        contact_label.setFont(QFont('Microsoft YaHei', 9))
        contact_label.setStyleSheet("color: #555;")
        info_layout.addWidget(contact_label)
        
        email_label = QLabel("邮箱: 18935590710@163.com")
        email_label.setFont(QFont('Microsoft YaHei', 9))
        email_label.setStyleSheet("color: #555;")
        info_layout.addWidget(email_label)
        
        note_label = QLabel("注: 请提供您的机器码，我们将为您生成专属注册码")
        note_label.setFont(QFont('Microsoft YaHei', 8, QFont.Weight.Light))
        note_label.setStyleSheet("color: #777; font-style: italic; margin-top: 5px;")
        info_layout.addWidget(note_label)
        
        layout.addLayout(info_layout)
        
        # 添加调试信息
        self.debug_info = QLabel()
        self.debug_info.setWordWrap(True)
        self.debug_info.setStyleSheet("color: #666; font-size: 8pt;")
        layout.addWidget(self.debug_info)
        
        # 绑定事件
        self.register_btn.clicked.connect(self.register)
        self.cancel_btn.clicked.connect(self.reject)
        
        self.setLayout(layout)
    
    def register(self):
        register_code = self.register_code_edit.text().strip()
        if not register_code:
            QMessageBox.warning(self, "警告", "请输入注册码！")
            return
        
        print(f"\n开始注册验证:")
        print(f"机器码: {self.machine_code}")
        print(f"注册码: {register_code}")
        
        try:
            # 手动验证一次，以便进行详细调试
            parts = register_code.split('-')
            if len(parts) != 6:
                print(f"注册码格式错误: 期望6个部分，实际{len(parts)}个部分")
            else:
                # 解析各部分
                prefix, code_part1, signature, expire_timestamp, code_part2, encrypted_part = parts
                print(f"注册码解析结果:")
                print(f"前缀: {prefix}")
                print(f"代码部分1: {code_part1}")
                print(f"签名: {signature}")
                print(f"过期时间戳: {expire_timestamp}")
                print(f"代码部分2: {code_part2}")
                print(f"加密部分: {encrypted_part}")
                
            # 调用注册方法
            if self.auth_manager.register(register_code):
                QMessageBox.information(self, "成功", "注册成功！")
                self.accept()
            else:
                QMessageBox.critical(self, "错误", "注册码无效或已过期")
        except Exception as e:
            print(f"注册过程中发生错误: {e}")
            QMessageBox.critical(self, "错误", f"注册过程中发生错误: {e}")
    
    def get_machine_code(self):
        return self.machine_code