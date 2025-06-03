import os
import json
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGroupBox,
    QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator

class ParameterWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("参数设置")
        self.resize(400, 350)
        
        # 默认参数值
        self.default_params = {
            "h_a": 0.6,
            "h_b": 0.6,
            "k": 0.14,
            "pc": -0.28,
            "mc": -2.43,
            "r": 6371000,
            "tolerance_factor": 40  # 添加tolerance系数默认值
        }
        
        # 加载已保存的参数
        self.params = self.load_parameters()
        
        self.init_ui()
        self.populate_fields()
        self.center_window()
        
    def center_window(self):
        """将窗口置于屏幕中央"""
        frame_geometry = self.frameGeometry()
        screen_center = self.screen().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())
        
    def init_ui(self):
        """初始化用户界面"""
        main_layout = QVBoxLayout()
        
        # 创建参数组
        params_group = QGroupBox("测量参数")
        form_layout = QFormLayout()
        
        # 创建字段并添加验证器
        self.h_a_edit = QLineEdit()
        self.h_a_edit.setValidator(QDoubleValidator())
        form_layout.addRow("h_a (相对空气湿度A):", self.h_a_edit)
        
        self.h_b_edit = QLineEdit()
        self.h_b_edit.setValidator(QDoubleValidator())
        form_layout.addRow("h_b (相对空气湿度B):", self.h_b_edit)
        
        self.k_edit = QLineEdit()
        self.k_edit.setValidator(QDoubleValidator())
        form_layout.addRow("k (大气折光系数):", self.k_edit)
        
        self.pc_edit = QLineEdit()
        self.pc_edit.setValidator(QDoubleValidator())
        form_layout.addRow("pc (加法常数改正):", self.pc_edit)
        
        self.mc_edit = QLineEdit()
        self.mc_edit.setValidator(QDoubleValidator())
        form_layout.addRow("mc (乘法常数改正):", self.mc_edit)
        
        self.r_edit = QLineEdit()
        self.r_edit.setValidator(QDoubleValidator())
        form_layout.addRow("r (地球半径/m):", self.r_edit)

        # 添加tolerance系数输入框，使用水平布局添加后缀说明
        self.tolerance_factor_edit = QLineEdit()
        self.tolerance_factor_edit.setValidator(QDoubleValidator())
        
        # 创建水平布局来包含输入框和说明标签
        tolerance_layout = QHBoxLayout()
        tolerance_layout.addWidget(self.tolerance_factor_edit)
        
        # 添加说明标签
        tolerance_suffix = QLabel("× √边长")
        tolerance_suffix.setStyleSheet("font-weight: bold;")
        tolerance_layout.addWidget(tolerance_suffix)
        tolerance_layout.addStretch()  # 添加弹性空间，确保标签紧贴输入框
        
        # 将水平布局添加到表单布局
        form_layout.addRow("限差:", tolerance_layout)
        
        params_group.setLayout(form_layout)
        main_layout.addWidget(params_group)
        
        # 添加说明标签
        description = QLabel("这些参数用于三角高程测量计算。\n修改后点击保存，重启程序后生效。")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(description)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 保存按钮
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.save_parameters)
        button_layout.addWidget(save_button)
        
        # 重置按钮
        reset_button = QPushButton("重置为默认")
        reset_button.clicked.connect(self.reset_to_default)
        button_layout.addWidget(reset_button)
        
        # 取消按钮
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        
    def populate_fields(self):
        """从配置中填充字段"""
        self.h_a_edit.setText(str(self.params["h_a"]))
        self.h_b_edit.setText(str(self.params["h_b"]))
        self.k_edit.setText(str(self.params["k"]))
        self.pc_edit.setText(str(self.params["pc"]))
        self.mc_edit.setText(str(self.params["mc"]))
        self.r_edit.setText(str(self.params["r"]))
        self.tolerance_factor_edit.setText(str(self.params["tolerance_factor"]))  # 设置tolerance系数值
        
    def reset_to_default(self):
        """重置为默认参数"""
        self.params = self.default_params.copy()
        self.populate_fields()
        QMessageBox.information(self, "重置成功", "已重置为默认参数，点击保存后生效。")
        
    def load_parameters(self):
        """加载参数配置"""
        config_dir = os.path.join(os.path.expanduser("~"), ".tl_tools")
        config_file = os.path.join(config_dir, "parameters.json")
        
        # 如果配置文件不存在，使用默认值
        if not os.path.exists(config_file):
            return self.default_params.copy()
        
        try:
            with open(config_file, 'r') as f:
                params = json.load(f)
                
            # 确保所有必要的参数都存在
            for key in self.default_params:
                if key not in params:
                    params[key] = self.default_params[key]
                    
            return params
        except Exception as e:
            QMessageBox.warning(self, "加载失败", f"无法加载参数设置: {str(e)}\n将使用默认参数。")
            return self.default_params.copy()
        
    def save_parameters(self):
        """保存参数配置"""
        try:
            # 收集参数
            params = {
                "h_a": float(self.h_a_edit.text()),
                "h_b": float(self.h_b_edit.text()),
                "k": float(self.k_edit.text()),
                "pc": float(self.pc_edit.text()),
                "mc": float(self.mc_edit.text()),
                "r": float(self.r_edit.text()),
                "tolerance_factor": float(self.tolerance_factor_edit.text())  # 保存tolerance系数值
            }
            
            # 创建配置目录
            config_dir = os.path.join(os.path.expanduser("~"), ".tl_tools")
            os.makedirs(config_dir, exist_ok=True)
            
            # 保存到配置文件
            config_file = os.path.join(config_dir, "parameters.json")
            with open(config_file, 'w') as f:
                json.dump(params, f, indent=4)
                
            QMessageBox.information(self, "保存成功", "参数设置已保存，重启程序后生效。")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"无法保存参数设置: {str(e)}") 