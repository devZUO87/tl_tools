# 三角高程测量软件开发
三角高程软件开发

## 开发日志

### 2023-xx-xx：项目初始化
- 创建了基本项目结构
- 设置了PyQt6作为UI框架

### 2023-xx-xx：添加完善的.gitignore文件
- **会话主要目的**：优化项目的版本控制配置
- **完成的主要任务**：创建了适合Python和PyQt6项目的完整.gitignore文件
- **关键决策和解决方案**：
  - 添加了Python特定的忽略规则（如__pycache__、*.py[cod]）
  - 添加了PyQt6相关的忽略规则（如*_ui.py、*_rc.py）
  - 配置了IDE、虚拟环境和临时文件的忽略规则
- **使用的技术栈**：Git版本控制
- **修改的文件**：.gitignore

### 2023-xx-xx：优化.gitignore文件
- **会话主要目的**：明确指定忽略.pyc编译文件
- **完成的主要任务**：在.gitignore中添加了明确的.pyc文件忽略规则
- **关键决策和解决方案**：
  - 虽然`*.py[cod]`模式已经包含了.pyc文件，但为了更明确，添加了专门的`*.pyc`规则
- **使用的技术栈**：Git版本控制
- **修改的文件**：.gitignore

### 2024-xx-xx：实现完整日志系统
- **会话主要目的**：实现应用程序的日志功能
- **完成的主要任务**：将已有的日志模块集成到应用程序的各个组件中
- **关键决策和解决方案**：
  - 在主要应用程序入口点（main.py）添加日志记录
  - 在主窗口类（MainWindow）中添加操作和错误日志
  - 在可拖拽表格组件（DraggableTableWidget）中添加性能监控和错误处理
  - 使用装饰器对关键方法进行性能监控
  - 实现异常捕获并记录到错误日志
- **使用的技术栈**：
  - Python logging模块
  - 线程安全的单例模式日志管理器
  - 性能监控（CPU、内存、执行时间）
  - JSON格式化日志
- **修改的文件**：
  - main.py
  - src/widgets/main_window.py
  - src/widgets/draggable_table_widgets.py

### 2024-xx-xx：修复菜单事件处理错误
- **会话主要目的**：修复菜单事件处理时的参数错误
- **完成的主要任务**：解决了 `TypeError: MainWindow.importMatchingTable() takes 1 positional argument but 2 were given` 错误
- **关键决策和解决方案**：
  - 为所有与菜单/按钮关联的方法添加了 `*args` 参数，以接收 PyQt 自动传递的事件参数
  - 修复了 `importMatchingTable`, `openFile`, `exportOutsideTable`, `set_draggable_table_widget`, `calculate_draggable_table_widget`, `showAbout` 和 `set_parameter` 方法
- **使用的技术栈**：
  - PyQt6 事件处理机制
- **修改的文件**：
  - src/widgets/main_window.py

### 2024-xx-xx：参数化tolerance计算系数
- **会话主要目的**：将限差计算中的tolerance系数从硬编码改为可配置参数
- **完成的主要任务**：
  - 在参数设置窗口中添加tolerance_factor参数
  - 修改计算逻辑使用参数化的系数
- **关键决策和解决方案**：
  - 将原本硬编码的40系数提取为可在UI中配置的参数
  - 在MainWindow中添加参数加载和应用逻辑
  - 设置参数后能即时重新计算应用新参数
- **使用的技术栈**：
  - PyQt6配置界面
  - JSON参数持久化
- **修改的文件**：
  - src/widgets/parameter_window.py
  - src/widgets/main_window.py

### 2024-xx-xx：优化限差参数显示
- **会话主要目的**：改进限差参数的显示，增加公式说明
- **完成的主要任务**：
  - 在限差参数输入框后添加公式说明"× √边长"
- **关键决策和解决方案**：
  - 创建了水平布局来包含输入框和公式说明标签
  - 使用样式表设置公式标签的粗体显示，增强可读性
  - 保持了整体参数设置窗口的整洁布局
- **使用的技术栈**：
  - PyQt6 布局管理
  - Qt样式表
- **修改的文件**：
  - src/widgets/parameter_window.py
