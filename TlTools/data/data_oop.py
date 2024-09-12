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
        # 数据转换
        for key, value in self.original_list:
            station = self.group_by_type(key)
            for i in range(value.shape[0]):
                self.original_data.append([
                    key,
                    station,
                    self.group_by_type(value.iloc[i, 0]),
                    float(value.iloc[i, 4]),
                    float(value.iloc[i, 5]),
                    float(value.iloc[i, 6]),
                ])


    def get_grouped_data(self):
        # 根据 i1 和 i2 分组，返回分组后的数据
        for value in self.original_data:
            group_key = (value[1], value[2])
            self.grouped_data[group_key].append(value)


if __name__ == '__main__':
    path = 'D:/tl_tools/数据/jc'
    example = MeasurementData(path)
    grouped_data = example.grouped_data
    original_data = example.original_data
    original_list = example.original_list
    print(grouped_data)
    print(original_list)
    print(original_data)



    # for group_key, group_values in grouped_data.items():
    #     print(f"Group {group_key}:")
    #     for i, 数据 in enumerate(group_values):
    #         print(f"  Data {i + 1}: {数据}")
# grouped_data = defaultdict(<class 'list'>,
# {('JS02', 'KZ01'): [['JS02-0518', 'JS02', 'KZ01', 0.0, 84.39391, 454.44305],
#                     ['JS02-0519', 'JS02', 'KZ01', 0.0, 84.39384, 454.43776875],
#                     ['JS02-0520', 'JS02', 'KZ01', 0.0, 84.37235, 454.4947916666667],
#                     ['JS02SS2-0520', 'JS02', 'KZ01', 0.0, 89.46164, 817.4432666666668]],
#  ('JS02', 'KZ02'): [['JS02S-0518', 'JS02', 'KZ02', 0.0, 86.38596, 731.0715124999999],
#                     ['JS02S-0520', 'JS02', 'KZ02', 0.0, 86.39069, 731.0709],
#                     ['JS02SS-0520', 'JS02', 'KZ02', 0.0, 86.3906, 731.0705791666668]],
#  ('KZ02', 'JS03'): [['KZ02-0518', 'KZ02', 'JS03', 0.0, 94.32126, 594.4821625]],
#  ('KZ03', 'KZ02'): [['KZ03-0518', 'KZ03', 'KZ02', 0.0, 85.28425, 594.43890625],
#                     ['KZ03-0519', 'KZ03', 'KZ02', 0.0, 85.2836, 594.43970625],
#                     ['KZ03-0520', 'KZ03', 'KZ02', 0.0, 85.28345, 594.4427708333334]],
#  ('KZ03', 'KZ01'): [['KZ03S-0518', 'KZ03', 'KZ01', 0.0, 85.37295, 608.42556875],
#                     ['KZ03S-0519', 'KZ03', 'KZ01', 0.0, 85.37179, 608.42435],
#                     ['KZ03S-0520', 'KZ03', 'KZ01', 0.0, 85.35392, 608.4769291666667]],
#  ('KZ03', 'JS03'): [['KZ03SS-0518', 'KZ03', 'JS03', 0.0, 85.58585, 542.64929375]],
#  ('JS03', 'KZ03'): [['JS03-0519', 'JS03', 'KZ03', 0.0, 94.02205, 542.6668875],
#                     ['JS03S-0520', 'JS03', 'KZ03', 0.0, 94.01076, 542.6499375]],
#  ('KZ01', 'KZ02'): [['KZ01-0519', 'KZ01', 'KZ02', 0.0, 89.59415, 1157.61235625],
#                     ['KZ01-0520', 'KZ01', 'KZ02', 0.0, 89.59451, 1157.6189125],
#                     ['KZ01S-0520', 'KZ01', 'KZ02', 0.0, 89.5929, 1157.616983333333]],
#  ('KZ01', 'KZ03'): [['KZ01S-0519', 'KZ01', 'KZ03', 0.0, 94.2523, 608.4656625]],
#  ('KZ01', 'JS02'): [['KZ01S-0519', 'KZ01', 'JS02', 359.58548, 95.22223, 454.47635625]],
#  ('KZ02', 'KZ03'): [['KZ02-0519', 'KZ02', 'KZ03', 0.0, 94.32273, 594.46360625],
#                     ['KZ02S1-0520', 'KZ02', 'KZ03', 0.0, 94.30519, 594.438]],
#  ('KS02', 'KZ01'): [['KS02S-0519', 'KS02', 'KZ01', 0.0, 90.0124, 1157.61195625]],
#  ('KS03', 'JS03'): [['KS03SS-0519', 'KS03', 'JS03', 0.0, 85.58538, 542.651375],
#                     ['KS03SS-0519', 'KS03', 'JS03', 269.5957, 85.58554, 542.6513500000001]],
#  ('JS02', 'JS02'): [['JS02SS1-0520', 'JS02', 'JS02', 0.0, 93.20349, 731.0706291666667]],
#  ('JS03', 'JS02'): [['JS03-0520', 'JS03', 'JS02', 0.0, 92.52502, 676.3338916666667]],
#  ('KZ02', 'KZ01'): [['KZ02-0520', 'KZ02', 'KZ01', 0.0, 90.00212, 1157.61936875],
#                     ['KZ02S-0520', 'KZ02', 'KZ01', 0.0, 90.00211, 1157.61865]],
#  ('KZ02', 'JS02'): [['KZ02SS-0520', 'KZ02', 'JS02', 0.0, 93.20394, 731.0725708333333]]})
#
# original_data = [['JS02-0518', 'JS02', 'KZ01', 0.0, 84.39391, 454.44305],
#     ['JS02S-0518', 'JS02', 'KZ02', 0.0, 86.38596, 731.0715124999999],
#     ['KZ02-0518', 'KZ02', 'JS03', 0.0, 94.32126, 594.4821625],
#     ['KZ03-0518', 'KZ03', 'KZ02', 0.0, 85.28425, 594.43890625],
#     ['KZ03S-0518', 'KZ03', 'KZ01', 0.0, 85.37295, 608.42556875],
#     ['KZ03SS-0518', 'KZ03', 'JS03', 0.0, 85.58585, 542.64929375],
#     ['JS02-0519', 'JS02', 'KZ01', 0.0, 84.39384, 454.43776875],
#     ['JS03-0519', 'JS03', 'KZ03', 0.0, 94.02205, 542.6668875],
#     ['KZ01-0519', 'KZ01', 'KZ02', 0.0, 89.59415, 1157.61235625],
#     ['KZ01S-0519', 'KZ01', 'KZ03', 0.0, 94.2523, 608.4656625],
#     ['KZ01S-0519', 'KZ01', 'JS02', 359.58548, 95.22223, 454.47635625],
#     ['KZ02-0519', 'KZ02', 'KZ03', 0.0, 94.32273, 594.46360625],
#     ['KS02S-0519', 'KS02', 'KZ01', 0.0, 90.0124, 1157.61195625],
#     ['KZ03-0519', 'KZ03', 'KZ02', 0.0, 85.2836, 594.43970625],
#     ['KZ03S-0519', 'KZ03', 'KZ01', 0.0, 85.37179, 608.42435],
#     ['KS03SS-0519', 'KS03', 'JS03', 0.0, 85.58538, 542.651375],
#     ['KS03SS-0519', 'KS03', 'JS03', 269.5957, 85.58554, 542.6513500000001],
#     ['JS02-0520', 'JS02', 'KZ01', 0.0, 84.37235, 454.4947916666667],
#     ['JS02S-0520', 'JS02', 'KZ02', 0.0, 86.39069, 731.0709],
#     ['JS02SS-0520', 'JS02', 'KZ02', 0.0, 86.3906, 731.0705791666668],
#     ['JS02SS1-0520', 'JS02', 'JS02', 0.0, 93.20349, 731.0706291666667],
#     ['JS02SS2-0520', 'JS02', 'KZ01', 0.0, 89.46164, 817.4432666666668],
#     ['JS03-0520', 'JS03', 'JS02', 0.0, 92.52502, 676.3338916666667],
#     ['JS03S-0520', 'JS03', 'KZ03', 0.0, 94.01076, 542.6499375],
#     ['KZ01-0520', 'KZ01', 'KZ02', 0.0, 89.59451, 1157.6189125],
#     ['KZ01S-0520', 'KZ01', 'KZ02', 0.0, 89.5929, 1157.616983333333],
#     ['KZ02-0520', 'KZ02', 'KZ01', 0.0, 90.00212, 1157.61936875],
#     ['KZ02S-0520', 'KZ02', 'KZ01', 0.0, 90.00211, 1157.61865],
#     ['KZ02S1-0520', 'KZ02', 'KZ03', 0.0, 94.30519, 594.438],
#     ['KZ02SS-0520', 'KZ02', 'JS02', 0.0, 93.20394, 731.0725708333333],
#     ['KZ03-0520', 'KZ03', 'KZ02', 0.0, 85.28345, 594.4427708333334],
#     ['KZ03S-0520', 'KZ03', 'KZ01', 0.0, 85.35392, 608.4769291666667]]
