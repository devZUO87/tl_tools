import os
from collections import defaultdict

import pandas as pd


class MeasurementData:
    def __init__(self, path):
        self.original_list = []
        self.original_data = []
        self.temp_files = []
        self.path = path
        self.grouped_data = defaultdict(list)  # 使用 defaultdict(list) 以便直接添加数据
        self.process_directory()
        self.data_transform()
        self.cleanup_temp_files()
        self.get_grouped_data()

    def process_directory(self):
        for root, dirs, files in os.walk(self.path):
            for file in files:
                if file.endswith('.xls'):
                    file_path = os.path.join(root, file)
                    data = pd.read_excel(file_path)
                    temp_file_path = file_path.replace(".xls", "_temp.xlsx")
                    data.to_excel(temp_file_path, index=False)
                    self.temp_files.append(temp_file_path)

        for root, dirs, files in os.walk(self.path):
            for file in files:
                if file.endswith('_temp.xlsx'):
                    file_path = os.path.join(root, file)
                    # 获取文件所在的上一级目录名称作为附加信息
                    last_dir = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
                    # 获取文件名(去掉_temp.xlsx)作为基础文件名
                    file_name = file[:-10]
                    # 读取Excel文件数据
                    data = pd.read_excel(file_path)
                    # 组合文件名和目录名，形成标识符
                    name = file_name + '-' + last_dir
                    # 选择尾部6行数据，并且只取有效列（从第2列开始，排除最后4列）
                    # 这里通常包含测量结果数据
                    selected_rows = data.tail(6).iloc[:, 1:-4]
                    # 获取第一列的列名（通常包含目标点信息）
                    column_name = selected_rows.columns[0]
                    # 移除第一列为空的行（确保有目标点信息）
                    selected_rows = selected_rows.dropna(subset=[column_name])
                    # 转换为DataFrame，只保留值（不保留原始列名）
                    df = pd.DataFrame(selected_rows.values)
                    # 重置列名为空（后续处理中会提取实际有意义的信息）
                    df.columns = [''] * len(df.columns)
                    # 将处理后的数据与文件标识符一起保存
                    self.original_list.append((name, df))

    def cleanup_temp_files(self):
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def group_by_type(self, s):
        """
        识别并提取字符串中的特定模式（通常是测站或目标点标识）
        
        工作原理：
        1. 将字符串分组为数字、字母和符号
        2. 返回前两组字符（通常是站点编号的主要部分）
        
        例如：
        - "A123-XYZ" 会被识别为 "A123"
        - "T45(南)" 会被识别为 "T45"
        """
        if not s:
            return ""

        groups = []
        current_group = s[0]

        def char_type(c):
            """判断字符类型：数字、字母或符号"""
            if c.isdigit():
                return 'digit'
            elif c.isalpha():
                return 'alpha'
            else:
                return 'symbol'

        # 按字符类型分组
        for i in range(1, len(s)):
            if char_type(s[i]) == char_type(current_group[-1]):
                current_group += s[i]
            else:
                groups.append(current_group)
                current_group = s[i]

        groups.append(current_group)
        # 返回前两组字符（通常是字母+数字或数字+字母的组合）
        # 例如："T45(南)" 会返回 "T45"
        return groups[0] + groups[1] if len(groups) > 1 else groups[0]

    def data_transform(self):
        """
        将原始数据转换为结构化格式
        
        每行数据包含：
        - 文件标识符
        - 测站ID（从文件名提取）
        - 目标ID（从数据第一列提取）
        - 归零方向均值（数据第5列）
        - 天顶角均值（数据第6列）
        - 斜距（数据第7列）
        """
        # 数据转换
        for key, value in self.original_list:
            # 从文件标识符中提取测站ID
            station = self.group_by_type(key)
            for i in range(value.shape[0]):
                self.original_data.append([
                    key,  # 文件标识符
                    station,  # 测站ID
                    self.group_by_type(value.iloc[i, 0]),  # 目标ID（从第一列提取）
                    float(value.iloc[i, 4]),  # 归零方向均值（第5列）
                    float(value.iloc[i, 5]),  # 天顶角均值（第6列）
                    float(value.iloc[i, 6]),  # 斜距（第7列）
                ])


    def get_grouped_data(self):
        """
        按测站和目标对数据进行分组
        
        分组键为(测站ID, 目标ID)的元组
        这样可以将同一测站对同一目标的多次测量分到一组
        """
        # 根据测站ID和目标ID分组，返回分组后的数据
        for value in self.original_data:
            group_key = (value[1], value[2])  # 使用(测站ID, 目标ID)作为分组键
            self.grouped_data[group_key].append(value)


if __name__ == '__main__':
    path = 'E:/个人/PYPROJECT/tl_tools/数据/JS02STEST'
    example = MeasurementData(path)
    print(example.original_data)
