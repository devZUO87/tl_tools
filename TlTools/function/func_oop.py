import math


class Measurement:
    def __init__(self, s, z, i, l, t_a, t_b, p_a, p_b, h_a=0.6, h_b=0.6, k=0.14, pc=-0.28, mc=-2.43, r=6371000):
        self.s = s
        self.z = z
        self.i = i
        self.l = l
        self.t_a = t_a
        self.t_b = t_b
        self.p_a = p_a
        self.p_b = p_b
        self.h_a = h_a
        self.h_b = h_b
        self.k = k
        self.pc = pc
        self.mc = mc
        self.r = r
        self.decimal_degrees = 0
        self.mcd = 0
        self.s_correction = 0
        self.d = 0
        self.h = 0
        self.meteorological_correction()
        self.constant_correction()
        self.dms_to_degrees()
        self.slope_distance_to_horizontal_distance()
        self.calculate_height_by_one_side_k()

    def dms_to_degrees(self):
        # 将度.分秒字符串分割为度、分、秒部分
        # 将度分秒格式转换为十进制度
        degrees = int(self.z)
        minutes = int((self.z - degrees) * 100)
        seconds = (((self.z - degrees) * 100) - minutes) * 100

        # 计算十进制度
        self.decimal_degrees = degrees + minutes / 60 + seconds / 3600

    def meteorological_correction(self):
        """
        计算气象学改正
        """
        p = (self.p_a + self.p_b) / 2
        t = (self.t_a + self.t_b) / 2
        h = (self.h_a + self.h_b) / 2
        x = 7.5 * t / (t + 237.3) + 0.7857
        a = 1 / 273.15
        # dd为mm每km
        dd = 286.34 - (0.29525 * p / (1 + a * t) -
                       4.126 * 10 ** (-4) * h / (1 + a * t) * 10 ** x)
        self.mcd = self.s * (1 + dd / 1000000)

    def constant_correction(self):
        """
        计算加乘常数改正为总改正
        """
        self.s_correction = self.mcd * (1 + self.mc * 10 ** (-6)) + self.pc / 1000

    def slope_distance_to_horizontal_distance(self):
        """
        斜距计算水平距离
        :return:d 水平距离
        """
        self.d = self.s_correction * math.sin(self.decimal_degrees * (math.pi / 180))

    def calculate_height_by_one_side_k(self):
        """
        通过一边斜距计算高
        :return: h 高
        """
        self.h = (self.d / math.tan(self.decimal_degrees * (math.pi / 180)) + self.i - self.l +
                  (1 - self.k) * (self.d ** 2) / (2 * self.r))


example1 = Measurement(1304.21906666667, 95.55329, 1.1510, 1.318, 25.2, 24.8, 861, 874)
print(example1.s_correction, example1.h)
