import math

pc = -0.28
mc = -2.43


# 度转度分秒
def to_dms(degrees):
    abs_degrees = abs(degrees)
    d = int(abs_degrees)
    m = int((abs_degrees - d) * 60)
    s = (abs_degrees - d - m / 60) * 3600
    sign = -1 if degrees < 0 else 1
    d = d * sign

    # 格式化为度分秒字符串，并确保分和秒前面补零且秒保留四位小数
    dms_str = f"{d}°{m:02}′{s:.2f}″"

    # 创建不包含符号的格式化字符串
    dms = dms_str.replace(".", "").replace("°", ".").replace("′", "").replace("″", "")

    return dms_str, dms


def slope_distance_to_horizontal_distance(s, z, t_a, t_b, p_a, p_b, h_a, h_b):
    """
    斜距计算水平距离
    :param s: 测量出的斜距
    :param z: 天顶角
    :param t_a: 仪器温度
    :param t_b: 测站温度
    :param p_a: 仪器气压
    :param p_b: 测站气压
    :param h_a: 仪器湿度 default 0.6
    :param h_b: 测站湿度 default 0.6
    :return:d 水平距离
    """
    s_correction = total_correction(s, t_a, t_b, p_a, p_b, h_a, h_b)
    z_degree = dms_to_degrees(z)
    d = s_correction * math.sin(z_degree * (math.pi / 180))
    return d


def dms_to_degrees(dms):
    # 将度分秒字符串分割为度、分、秒部分
    # 将度分秒格式转换为十进制度
    degrees = int(dms)
    minutes = int((dms - degrees) * 100)
    seconds = (((dms - degrees) * 100) - minutes) * 100

    # 计算十进制度
    decimal_degrees = degrees + minutes / 60 + seconds / 3600
    return decimal_degrees


def meteorological_correction(s, t1, t2, p1, p2, h_a=0.6, h_b=0.6):
    """
    计算气象学改正
    :param s: 斜距
    :param t1: 仪器温度
    :param t2: 测站温度
    :param p1: 仪器气压
    :param p2: 测站气压
    :param h_a: 仪器湿度 default 0.6
    :param h_b: 测站湿度 default 0.6
    :return: 气象学改正
    """

    p = (p1 + p2) / 2
    t = (t1 + t2) / 2
    h = (h_a + h_b) / 2
    x = 7.5 * t / (t + 237.3) + 0.7857
    a = 1 / 273.15
    # dd为mm每km
    dd = 286.34 - (0.29525 * p / (1 + a * t) -
                   4.126 * 10 ** (-4) * h / (1 + a * t) * 10 ** x)
    mcd = s * (1 + dd / 1000000)
    return mcd


def constant_correction(mcd):
    """
    计算加乘常数改正
    :param mcd: 气象学改正
    :return: 加乘常数改正
    """
    ccd = mcd * (1 + mc * 10 ** (-6)) + pc / 1000
    return ccd


def total_correction(s, t1, t2, p1, p2, h1=0.6, h2=0.6):
    """
    计算总改正
    :param s: 测得斜距
    :param t1: 仪器温度
    :param t2: 测站温度
    :param p1: 仪器气压
    :param p2: 测站气压
    :param h1: 仪器湿度 default 0.6
    :param h2: 测站湿度 default 0.6
    :return: 总改正
    """
    # 计算气象学改正
    mcd = meteorological_correction(s, t1, t2, p1, p2, h1, h2)
    # 计算加乘常数改正
    s_correction = constant_correction(mcd)
    return s_correction


def calculate_refractive_index_by_both_side(s1, s2, z_ab, z_ba, i_a, l_a, i_b, l_b, t1, t2, p1, p2, h1=0.6, h2=0.6):
    d_ab = slope_distance_to_horizontal_distance(s1, z_ab, t1, t1, p1, p1, h1, h1)
    d_ba = slope_distance_to_horizontal_distance(s2, z_ba, t2, t2, p2, p2, h2, h2)
    d = 1 / 2 * (d_ab + d_ba)
    # 计算往测总改正
    s_ab = total_correction(s1, t1, t1, p1, p1, h1, h2)
    # 计算返测总改正
    s_ba = total_correction(s2, t2, t2, p2, p2, h1, h2)
    # 将度分秒转换为度
    z_ab = dms_to_degrees(z_ab)
    z_ba = dms_to_degrees(z_ba)
    # 计算AB方向的水平距离

    r = 6371000
    k = 1 + r * (
            (s_ab * math.cos(math.radians(z_ab)) +
             s_ba * math.cos(math.radians(z_ba))) +
            (i_a - l_b) + (i_b - l_a)) / (d ** 2)
    # k = 1 + r * (
    #         (s_ab * math.cos(z_ab*(math.pi / 180)) +
    #          s_ba * math.cos(z_ba*(math.pi / 180))) +
    #         (i_a - l_b) + (i_b - l_a)) / (d ** 2)
    print(z_ab, z_ba, d, k)
    return k


#
#
def calculate_height_by_both_side_k(s_ab, s_ba, z_ab, z_ba, i_a, l_a, i_b, l_b, t_ab, t_ba, p_ab, p_ba, h_ab, h_ba):
    """
    计算双向高差
    :param s_ab:AB方向的斜距
    :param s_ba:BA方向的斜距
    :param z_ab:AB方向的天顶角
    :param z_ba:BA方向的天顶角
    :param i_a:仪器高
    :param i_b:测站高
    :param l_a:仪器高
    :param l_b:测站高
    :param t_ab:AB方向的平均温度
    :param t_ba:BA方向的平均温度
    :param p_ab:AB方向的平均气压
    :param p_ba:BA方向的平均气压
    :param h_ab:AB方向的平均湿度 default 0.6
    :param h_ba:BA方向的平均湿度 default 0.6
    :return:仪器和测站的高差
    """
    r = 6371000
    d_ab = slope_distance_to_horizontal_distance(s_ab, z_ab, t_ab, t_ab, p_ab, p_ab, h_ab, h_ab)
    d_ba = slope_distance_to_horizontal_distance(s_ba, z_ba, t_ba, t_ba, p_ba, p_ba, h_ba, h_ba)
    d = 1 / 2 * (d_ab + d_ba)
    k_ab = k_ba = 0.14
    h = 1 / 2 * (d * 1 / math.tan(z_ab * (math.pi / 180)) - d * 1 / math.tan(z_ba * (math.pi / 180)) + (
            i_a - l_b) + (i_b - l_a) - (k_ab - k_ba) * d ** 2 / (2 * r))
    return h


# 利用已知高差计算遮光系数
def calculate_refractive_index_by_one_side(s_ab, d_ab, z_ab, i_a, l_b, h0):
    r = 6371000
    k = 1 + 2 * r * ((s_ab * math.cos(z_ab * (math.pi / 180)) + i_a - l_b) - h0) / (d_ab ** 2)
    return k


def calculate_height_by_one_side_k(s, z, i, l, t_a, t_b, p_a, p_b, h_a=0.6, h_b=0.6, k=0.14, r=6371000):
    """
    计算单向高差
    :param s:仪器测得的斜距
    :param z:仪器测得的天顶角
    :param i:仪器高
    :param l:测站高
    :param t_a: 仪器温度
    :param t_b: 测站温度
    :param p_a: 仪器气压
    :param p_b: 测站气压
    :param h_a: 仪器湿度 default 0.6
    :param h_b: 测站湿度 default 0.6
    :param k:  大气垂直折光系数 default 0.14
    :param r:  地球半径 default 6371000
    :return:仪器和测站的高差
    """
    z_degree = dms_to_degrees(z)
    d = slope_distance_to_horizontal_distance(s, z, t_a, t_b, p_a, p_b, h_a, h_b)
    h = d / math.tan(z_degree * (math.pi / 180)) + i - l + (1 - k) * (d ** 2) / (2 * r)
    return h


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    he1 = calculate_height_by_one_side_k(1304.21906666667, 95.55329, 1.1510, 1.318, 25.2, 24.8, 861, 874)
    he2 = calculate_height_by_one_side_k(1304.23821666667, 84.05089, 1.527, 1.364, 25.0, 25.8, 874, 861)
    k1 = calculate_refractive_index_by_both_side(1304.2191, 1304.23821666667, 95.55329, 84.05089, 1.1510, 1.318, 1.527,
                                                 1.364, 24.8, 25.8, 867.5, 869)
    print(he1, he2, (he1 - he2) / 2, (he1 + he2) * 1000, k1)
