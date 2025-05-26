import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QLineEdit, QFileDialog, 
                            QMessageBox, QGroupBox, QFormLayout, QDoubleSpinBox,
                            QCheckBox, QProgressBar, QFrame, QTableWidget, QTableWidgetItem,
                            QComboBox, QTabWidget)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor
from src.ui.arrowcombobox import ArrowComboBox
from PyQt6.QtWebEngineWidgets import QWebEngineView
import os
import pandas as pd

class PointProcessorUI(QWidget):
    """数据处理程序的用户界面"""
    history_tab_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_styles()
        
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
        
        # 设置窗口标题和大小
        self.setWindowTitle('海道测量数据质检工具')
        self.resize(800, 600)
        
        # 将窗口移动到屏幕中心
        screen = QApplication.primaryScreen().geometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)
        
        # 创建TabWidget
        self.main_tab = QTabWidget()
        # ========== 主页Tab ===========
        home_widget = QWidget()
        home_layout = QVBoxLayout()
        home_layout.setSpacing(15)
        home_layout.setContentsMargins(20, 20, 20, 20)
        # 检查点文件选择
        check_file_group = QGroupBox("检查点文件")
        check_file_layout = QHBoxLayout()
        check_file_layout.setSpacing(10)
        self.check_file_label = QLabel("检查点文件: 未选择")
        self.check_file_label.setStyleSheet("color: #7f8c8d;")
        self.select_check_file_btn = QPushButton("检查点文件")
        self.select_check_file_btn.setFixedWidth(160)
        check_file_layout.addWidget(self.check_file_label)
        check_file_layout.addWidget(self.select_check_file_btn)
        check_file_group.setLayout(check_file_layout)
        home_layout.addWidget(check_file_group)
        # 测点文件选择
        test_file_group = QGroupBox("测点文件")
        test_file_layout = QHBoxLayout()
        test_file_layout.setSpacing(10)
        self.test_file_label = QLabel("测点文件: 未选择")
        self.test_file_label.setStyleSheet("color: #7f8c8d;")
        self.select_test_file_btn = QPushButton("测点文件")
        self.select_test_file_btn.setFixedWidth(160)
        test_file_layout.addWidget(self.test_file_label)
        test_file_layout.addWidget(self.select_test_file_btn)
        test_file_group.setLayout(test_file_layout)
        home_layout.addWidget(test_file_group)
        # 参数设置组
        params_group = QGroupBox("参数设置")
        params_layout = QFormLayout()
        params_layout.setSpacing(15)
        self.scale_combo = ArrowComboBox()
        self.scale_combo.addItems(['1:500', '1:1000', '1:2000', '1:5000', '1:10000'])
        self.scale_combo.setFixedWidth(110)
        self.scale_combo.currentIndexChanged.connect(self._update_radius)
        self.radius_value = 0.5  # 默认值对应1:500的搜索半径
        depth_tolerance_info = QLabel(
            "海道规范：\n"
            "0<Z≤20 | 0.5\n"
            "20<Z≤30 | 0.6\n"
            "30<Z≤50 | 0.7\n"
            "50<Z≤100 | 1.5\n"
            "Z>100 | 3%Z"
        )
        depth_tolerance_info.setStyleSheet("color: #666; font-size: 9pt;")
        params_layout.addRow("比例尺:", self.scale_combo)
        params_layout.addRow("检测标准:", depth_tolerance_info)
        params_group.setLayout(params_layout)
        home_layout.addWidget(params_group)
        # 筛选选项
        option_group = QGroupBox("筛选选项")
        option_layout = QVBoxLayout()
        option_layout.setSpacing(10)
        self.filter_duplicate_test_points = QCheckBox("筛选重复测点（只保留与检查点距离最近的一个）")
        self.filter_duplicate_test_points.setChecked(True)
        self.auto_open_excel = QCheckBox("导出完成后自动打开Excel文件")
        self.auto_open_excel.setChecked(True)
        option_layout.addWidget(self.filter_duplicate_test_points)
        option_layout.addWidget(self.auto_open_excel)
        option_group.setLayout(option_layout)
        home_layout.addWidget(option_group)
        # 进度显示
        progress_group = QGroupBox("处理进度")
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(10)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p% - %v/%m")
        progress_layout.addWidget(self.progress_bar)
        progress_group.setLayout(progress_layout)
        home_layout.addWidget(progress_group)
        # 操作按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        self.find_nearest_btn = QPushButton("质量检查")
        self.find_nearest_btn.setFixedWidth(120)
        self.find_nearest_btn.setMinimumHeight(40)
        self.find_nearest_btn.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        self.generate_compare_btn = QPushButton("生成对比图")
        self.generate_compare_btn.setFixedWidth(120)
        self.generate_compare_btn.setMinimumHeight(40)
        self.generate_compare_btn.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        self.generate_compare_btn.hide()
        button_layout.addStretch()
        button_layout.addWidget(self.find_nearest_btn)
        button_layout.addWidget(self.generate_compare_btn)
        button_layout.addStretch()
        home_layout.addLayout(button_layout)
        # 状态显示
        self.status_label = QLabel("就绪")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d;")
        home_layout.addWidget(self.status_label)
        # 分隔线和联系方式
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #cccccc;")
        home_layout.addWidget(separator)
        contact_layout = QHBoxLayout()
        self.contact_label = QLabel("联系方式：微信/电话：18935590710   邮箱：18935590710@163.com")
        self.contact_label.setStyleSheet("color: #95a5a6; font-size: 9pt; padding: 5px;")
        self.contact_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        contact_layout.addWidget(self.contact_label)
        home_layout.addLayout(contact_layout)
        home_widget.setLayout(home_layout)
        self.main_tab.addTab(home_widget, "主页")
        # ========== 对比图Tab ===========
        self.scatter_tab_content = QLabel("请先进行质量检查")
        self.scatter_tab_content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scatter_webview = QWebEngineView()
        self.main_tab.addTab(self.scatter_tab_content, "对比图")
        # ========== 柱状图Tab ===========
        self.bar_tab_content = QLabel("请先进行质量检查")
        self.bar_tab_content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bar_webview = QWebEngineView()
        # 柱状图统计信息Label
        self.bar_info_label = QLabel("")
        self.bar_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bar_info_label.setStyleSheet("color: #888; font-size: 12px; padding: 2px 0 2px 0; margin: 0;")
        self.main_tab.addTab(self.bar_tab_content, "柱状图")
        # ========== 质检结果Tab ===========
        self.result_tab_content = QLabel("请先进行质量检查")
        self.result_tab_content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_webview = QWebEngineView()
        self.main_tab.addTab(self.result_tab_content, "质检结果")
        # ========== 历史记录Tab ===========
        self.history_tab_content = QLabel("暂无历史记录")
        self.history_tab_content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_tab.addTab(self.history_tab_content, "历史记录")
        # 设置主布局为TabWidget
        layout = QVBoxLayout()
        layout.addWidget(self.main_tab)
        self.setLayout(layout)
        
        # 添加阴影效果
        self.setWindowFlags(Qt.WindowType.Window)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        
        self.main_tab.currentChanged.connect(self._on_tab_changed)
        
    def show_message(self, title, message):
        """显示消息对话框"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #f8f9fa;
            }
            QMessageBox QLabel {
                color: #2c3e50;
                font-size: 10pt;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        msg.exec()
    
    def show_error(self, title, message):
        """显示错误对话框"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #f8f9fa;
            }
            QMessageBox QLabel {
                color: #2c3e50;
                font-size: 10pt;
            }
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        msg.exec()
    
    def update_status(self, message):
        """更新状态栏消息"""
        self.status_label.setText(message)
        QApplication.processEvents()
    
    def update_progress(self, value, maximum=None):
        """更新进度条"""
        if maximum is not None:
            self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)
        QApplication.processEvents()
    
    def reset_progress(self):
        """重置进度条"""
        self.progress_bar.setValue(0)
        QApplication.processEvents()
    
    def get_radius(self):
        """获取搜索半径"""
        return self.radius_value
    
    def is_filter_duplicate_points(self):
        """获取是否筛选重复测点的选项"""
        return self.filter_duplicate_test_points.isChecked()
    
    def is_auto_open_excel(self):
        """获取是否自动打开Excel文件的选项"""
        return self.auto_open_excel.isChecked()
    
    def select_single_file(self, title):
        """选择单个文件"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            title,
            "",
            "DAT文件 (*.dat);;Excel文件 (*.xlsx *.xls);;所有文件 (*.*)"
        )
        return file_name if file_name else None
    
    def select_output_file(self):
        """选择输出文件保存位置"""
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "保存结果",
            "",
            "Excel文件 (*.xlsx)"
        )
        return file_name if file_name else None

    def _update_radius(self):
        """根据比例尺更新搜索半径"""
        scale_text = self.scale_combo.currentText()
        scale = int(scale_text.split(':')[1])
        self.radius_value = scale / 1000  # 比例尺分母除以1000作为搜索半径（单位：米）

    def show_html_to_tab(self, html_path, tab_name):
        """根据tab名加载本地HTML到对应webview，未生成时显示提示"""
        abs_path = os.path.abspath(html_path)
        
        # 定义Tab配置
        tab_configs = {
            "对比图": {
                "content": self.scatter_tab_content,
                "webview": self.scatter_webview,
                "index": 1
            },
            "柱状图": {
                "content": self.bar_tab_content,
                "webview": self.bar_webview,
                "index": 2
            }
        }
        
        if tab_name in tab_configs:
            config = tab_configs[tab_name]
            idx = self.main_tab.indexOf(config["content"])
            if idx == -1:
                idx = self.main_tab.indexOf(config["webview"])
                
            if os.path.exists(abs_path):
                if self.main_tab.indexOf(config["webview"]) == -1:
                    self.main_tab.removeTab(idx)
                    self.main_tab.insertTab(config["index"], config["webview"], tab_name)
                config["webview"].load(QUrl.fromLocalFile(abs_path))
            else:
                if self.main_tab.indexOf(config["content"]) == -1:
                    self.main_tab.removeTab(idx)
                    self.main_tab.insertTab(config["index"], config["content"], tab_name)
                config["content"].setText("请先进行质量检查")

    def show_result_tab(self, data, tab_name="质检结果"):
        """
        支持传入DataFrame或Excel文件路径，自动显示到质检结果Tab。
        """
        try:
            if isinstance(data, pd.DataFrame):
                df = data.fillna("")
            else:
                df = pd.read_excel(data)
                df = df.fillna("")
            table = QTableWidget()
            table.setColumnCount(df.shape[1])
            table.setRowCount(df.shape[0])
            table.setHorizontalHeaderLabels(df.columns.tolist())
            for i in range(df.shape[0]):
                for j in range(df.shape[1]):
                    table.setItem(i, j, QTableWidgetItem(str(df.iloc[i, j])))
            self.add_or_replace_tab(tab_name, table)
        except Exception as e:
            self.show_error("错误", f"无法加载质检结果: {str(e)}")

    def _on_tab_changed(self, idx):
        if self.main_tab.tabText(idx) == "历史记录":
            self.history_tab_requested.emit()

    def add_or_replace_tab(self, tab_name, widget):
        idx = -1
        for i in range(self.main_tab.count()):
            if self.main_tab.tabText(i) == tab_name:
                idx = i
                break
        if idx == -1:
            self.main_tab.addTab(widget, tab_name)
            idx = self.main_tab.count() - 1
        else:
            self.main_tab.removeTab(idx)
            self.main_tab.insertTab(idx, widget, tab_name)
        # 只有当前不是目标tab时才切换，避免递归
        if self.main_tab.currentIndex() != idx:
            self.main_tab.setCurrentIndex(idx)

    def show_bar_info(self, info: str):
        """在柱状图Tab下方显示统计信息"""
        # 找到柱状图webview所在的Tab
        idx = self.main_tab.indexOf(self.bar_webview)
        if idx == -1:
            # webview还没插入，先插入
            idx = self.main_tab.indexOf(self.bar_tab_content)
            if idx != -1:
                self.main_tab.removeTab(idx)
                self.main_tab.insertTab(2, self.bar_webview, "柱状图")
                idx = 2
        # 获取当前widget
        widget = self.main_tab.widget(idx)
        # 如果不是布局，重新设置
        if not isinstance(widget, QWidget) or not hasattr(widget, 'layout'):
            container = QWidget()
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            layout.addWidget(self.bar_webview)
            layout.addWidget(self.bar_info_label)
            container.setLayout(layout)
            self.main_tab.removeTab(idx)
            self.main_tab.insertTab(idx, container, "柱状图")
        else:
            # 已经有布局，直接加label
            layout = widget.layout()
            if layout.indexOf(self.bar_info_label) == -1:
                layout.addWidget(self.bar_info_label)
        # 设置紧凑样式和一行显示
        self.bar_info_label.setText(info)