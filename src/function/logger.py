import logging
import os
import time
import functools
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable, Any
import psutil
import threading
from queue import Queue
import json

class PerformanceMonitor:
    """性能监控类"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.memory_start = None
        self.memory_end = None
        self.cpu_start = None
        self.cpu_end = None
        
    def start(self):
        """开始监控"""
        self.start_time = time.time()
        self.memory_start = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        self.cpu_start = psutil.Process().cpu_percent()
        
    def stop(self) -> dict:
        """停止监控并返回性能数据"""
        self.end_time = time.time()
        self.memory_end = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        self.cpu_end = psutil.Process().cpu_percent()
        
        return {
            'execution_time': self.end_time - self.start_time,
            'memory_usage': self.memory_end - self.memory_start,
            'cpu_usage': self.cpu_end - self.cpu_start
        }

class LogManager:
    """日志管理器"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.log_dir = Path('logs')
            self.log_dir.mkdir(exist_ok=True)
            
            # 创建日志文件
            self.operation_log = self._setup_logger('operation.log', '操作日志')
            self.error_log = self._setup_logger('error.log', '错误日志')
            self.performance_log = self._setup_logger('performance.log', '性能日志')
            
            # 性能数据队列
            self.performance_queue = Queue()
            self._start_performance_monitor()
    
    def _setup_logger(self, filename: str, logger_name: str) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        
        # 文件处理器
        file_handler = logging.FileHandler(
            self.log_dir / filename,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        return logger
    
    def _start_performance_monitor(self):
        """启动性能监控线程"""
        def monitor_thread():
            while True:
                try:
                    data = self.performance_queue.get()
                    if data is None:
                        break
                    self.performance_log.info(json.dumps(data))
                except Exception as e:
                    self.error_log.error(f"性能监控错误: {str(e)}")
                finally:
                    self.performance_queue.task_done()
        
        self.monitor_thread = threading.Thread(target=monitor_thread, daemon=True)
        self.monitor_thread.start()
    
    def log_operation(self, message: str, level: str = 'INFO'):
        """记录操作日志"""
        log_func = getattr(self.operation_log, level.lower())
        log_func(message)
    
    def log_error(self, error: Exception, context: str = ''):
        """记录错误日志"""
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'traceback': traceback.format_exc()
        }
        self.error_log.error(json.dumps(error_info, ensure_ascii=False))
    
    def log_performance(self, data: dict):
        """记录性能数据"""
        self.performance_queue.put(data)
    
    def performance_monitor(self, func: Callable) -> Callable:
        """性能监控装饰器"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            monitor = PerformanceMonitor()
            monitor.start()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                performance_data = monitor.stop()
                performance_data.update({
                    'function': func.__name__,
                    'timestamp': datetime.now().isoformat()
                })
                self.log_performance(performance_data)
        
        return wrapper
    
    def cleanup(self):
        """清理资源"""
        self.performance_queue.put(None)
        self.monitor_thread.join()

# 创建全局日志管理器实例
log_manager = LogManager()

def log_operation(message: str, level: str = 'INFO'):
    """记录操作日志的便捷函数"""
    log_manager.log_operation(message, level)

def log_error(error: Exception, context: str = ''):
    """记录错误日志的便捷函数"""
    log_manager.log_error(error, context)

def performance_monitor(func: Callable) -> Callable:
    """性能监控装饰器的便捷函数"""
    return log_manager.performance_monitor(func) 