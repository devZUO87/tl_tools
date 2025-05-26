import math


class Measurement:
    @staticmethod
    def calculate_all(s, z, i, l, t_a, t_b, p_a, p_b, h_a=0.6, h_b=0.6, k=0.14, pc=-0.28, mc=-2.43, r=6371000):
        # 气象学改正
        p = (p_a + p_b) / 2
        t = (t_a + t_b) / 2
        h = (h_a + h_b) / 2
        x = 7.5 * t / (t + 237.3) + 0.7857
        a = 1 / 273.15
        dd = 286.34 - (0.29525 * p / (1 + a * t) - 4.126 * 10 ** (-4) * h / (1 + a * t) * 10 ** x)
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
