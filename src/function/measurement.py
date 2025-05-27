import math
import os
import json


class Measurement:
    @staticmethod
    def load_parameters():
        """加载计算参数"""
        # 默认参数值
        default_params = {
            "h_a": 0.6,
            "h_b": 0.6,
            "k": 0.14,
            "pc": -0.28,
            "mc": -2.43,
            "r": 6371000
        }
        
        # 尝试从配置文件加载参数
        config_dir = os.path.join(os.path.expanduser("~"), ".tl_tools")
        config_file = os.path.join(config_dir, "parameters.json")
        
        # 如果配置文件不存在，使用默认值
        if not os.path.exists(config_file):
            return default_params
        
        try:
            with open(config_file, 'r') as f:
                params = json.load(f)
                
            # 确保所有必要的参数都存在
            for key in default_params:
                if key not in params:
                    params[key] = default_params[key]
                    
            return params
        except Exception:
            return default_params

    @staticmethod
    def calculate_all(s, z, i, l, t_a, t_b, p_a, p_b, h_a=None, h_b=None, k=None, pc=None, mc=None, r=None):
        # 加载参数设置
        params = Measurement.load_parameters()
        
        # 如果未提供参数，使用加载的参数
        h_a = h_a if h_a is not None else params["h_a"]
        h_b = h_b if h_b is not None else params["h_b"]
        k = k if k is not None else params["k"]
        pc = pc if pc is not None else params["pc"]
        mc = mc if mc is not None else params["mc"]
        r = r if r is not None else params["r"]
        
        # 气象学改正
        p = (p_a + p_b) / 2 
        # 温度改正
        t = (t_a + t_b) / 2
        # 湿度改正
        h = (h_a + h_b) / 2
        # 水汽压
        x = 7.5 * t / (t + 237.3) + 0.7857
        # 干空气的气体常数
        a = 1 / 273.15
        # 大气折射率
        dd = 286.34 - (0.29525 * p / (1 + a * t) - 4.126 * 10 ** (-4) * h / (1 + a * t) * 10 ** x)
        # 气象学改正
        mcd = s * (1 + dd / 1000000)

        # 加乘常数改正
        s_correction = mcd * (1 + mc * 10 ** (-6)) + pc / 1000

        # 角度转换为十进制度
        degrees = int(z)
        minutes = int((z - degrees) * 100)
        seconds = (((z - degrees) * 100) - minutes) * 100
        decimal_degrees = degrees + minutes / 60 + seconds / 3600

        # 斜距转换为水平距离
        d = s_correction * math.sin(decimal_degrees * (math.pi / 180))

        # 计算最终高度
        height = (d / math.tan(decimal_degrees * (math.pi / 180)) + i - l +
                  (1 - k) * (d ** 2) / (2 * r))

        return {
            "mcd": round(mcd,5),
            "s_correction": round(s_correction,5),
            "d":  round(d,5),
            "height": round(height,5)
        }
