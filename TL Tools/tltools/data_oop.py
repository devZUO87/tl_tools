import os
from collections import defaultdict
import pandas as pd

class MeasurementData:
    def __init__(self, path):
        self.original_list = []
        self.transform_data = []
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
                    last_dir = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
                    file_name = file[:-10]
                    data = pd.read_excel(file_path)
                    name = file_name + '-' + last_dir
                    selected_rows = data.tail(6).iloc[:, 1:-4]
                    column_name = selected_rows.columns[0]
                    selected_rows = selected_rows.dropna(subset=[column_name])
                    df = pd.DataFrame(selected_rows.values)
                    df.columns = [''] * len(df.columns)
                    self.original_list.append((name, df))

    def cleanup_temp_files(self):
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def group_by_type(self, s):
        if not s:
            return ""

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
        return groups[0] + groups[1]

    def data_transform(self):
        for key, value in self.original_list:
            station = self.group_by_type(key)
            for i in range(value.shape[0]):
                self.transform_data.append([
                    key,
                    station,
                    self.group_by_type(value.iloc[i, 0]),
                    float(value.iloc[i, 4]),
                    float(value.iloc[i, 5]),
                    float(value.iloc[i, 6]),
                ])


    def get_grouped_data(self):
        # 根据 i1 和 i2 分组，返回分组后的数据
        for value in self.transform_data:
            group_key = (value[1], value[2])
            self.grouped_data[group_key].append(value)


if __name__ == '__main__':
    path = 'D:/tl_tools/data/原始数据/test/20240624-1'
    example = MeasurementData(path)
    grouped_data = example.grouped_data


    # for group_key, group_values in grouped_data.items():
    #     print(f"Group {group_key}:")
    #     for i, data in enumerate(group_values):
    #         print(f"  Data {i + 1}: {data}")
