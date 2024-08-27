import os
from collections import defaultdict

import pandas as pd
import re



class MeasurementData:
    def __init__(self, path):
        self.original_list = []
        self.transform_data = []
        self.range_data = []
        self.temp_files = []
        self.path = path
        self.process_directory()
        self.data_transform()
        self.cleanup_temp_files()
        self.range_data_by_name()

    def process_directory(self):
        for root, dirs, files in os.walk(self.path):
            for file in files:
                if file.endswith('.xls'):
                    # 获取文件的完整路径
                    file_path = os.path.join(root, file)
                    # 读取表格文件
                    data = pd.read_excel(file_path)
                    # data.to_excel(file_path.replace(".xls", "_temp.xlsx"), index=False)
                    # 读取表格文件
                    temp_file_path = file_path.replace(".xls", "_temp.xlsx")
                    data.to_excel(temp_file_path, index=False)
                    self.temp_files.append(temp_file_path)  # 记录临时文件路径

                    # 读取表格文件
        for root, dirs, files in os.walk(self.path):
            for file in files:
                if file.endswith('_temp.xlsx'):
                    # 获取文件的完整路径
                    file_path = os.path.join(root, file)
                    last_dir = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
                    file_name = file[:-10]
                    # 读取表格文件
                    data = pd.read_excel(file_path)
                    name = file_name + '-' + last_dir
                    # 将数据存储到数组中
                    # 筛选数据 选择 DataFrame data 的最后 6 行，并从中提取第 2 列到倒数第 4 列（不包括倒数第 4 列）的所有列
                    selected_rows = data.tail(6).iloc[:, 1:-4]
                    # 获取列名
                    column_name = selected_rows.columns[0]
                    # 删除包含空值的行
                    selected_rows = selected_rows.dropna(subset=[column_name])
                    df = pd.DataFrame(selected_rows.values)
                    df.columns = range(df.shape[1])  # 重新分配列名为整数索引
                    df.columns = [''] * len(df.columns)
                    self.original_list.append((name, df))

    def cleanup_temp_files(self):
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def group_by_type(self,s):
        if not s:
            return []

        groups = []
        current_group = s[0]

        def char_type(c):
            if c.isdigit():
                return 'digit'
            elif c.isalpha():
                return 'alpha'
            else:
                return 'symbol'

        for i in range(1, len(s)):
            if char_type(s[i]) == char_type(current_group[-1]):
                current_group += s[i]
            else:
                groups.append(current_group)
                current_group = s[i]

        groups.append(current_group)
        return groups[0]+groups[1]

    def data_transform(self):
        for key, value in self.original_list:
            station = self.group_by_type(key)
            # 获取数据
            for i in range(value.shape[0]):
                self.transform_data.append([
                    key,
                    station,
                    self.group_by_type(value.iloc[i, 0]),
                    float(value.iloc[i, 4]),
                    float(value.iloc[i, 5]),
                    float(value.iloc[i, 6]),
                ])

    def range_data_by_name(self):
        grouped_data = defaultdict(list)
        for value in self.transform_data:
            grouped_data[value[1]].append(value)

        # 对每个组进行排序
        sorted_data = []
        for key in sorted(grouped_data.keys()):
            sorted_data.extend(sorted(grouped_data[key], key=lambda x: x[1]))
        self.transform_data = sorted_data

if __name__ == '__main__':
    path = 'D:/tl_tools/data/原始数据/test/20240624-1'
    example = MeasurementData(path)
