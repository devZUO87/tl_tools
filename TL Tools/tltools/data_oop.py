import os

import pandas as pd


class MeasurementData:
    def __init__(self, path):
        self.original_dict = {}
        self.transform_data = {}
        self.path = path
        self.process_directory()
        self.data_transform()

    def process_directory(self):
        for root, dirs, files in os.walk(self.path):
            for file in files:
                if file.endswith('.xls'):
                    # 获取文件的完整路径
                    file_path = os.path.join(root, file)
                    # 读取表格文件
                    data = pd.read_excel(file_path)
                    data.to_excel(file_path.replace(".xls", "_temp.xlsx"), index=False)
                    # 读取表格文件
                    # 读取表格文件
        for root, dirs, files in os.walk(self.path):
            for file in files:
                if file.endswith('.xlsx'):
                    # 获取文件的完整路径
                    file_path = os.path.join(root, file)
                    last_dir = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
                    file_name = file[:-10]
                    # 读取表格文件
                    data = pd.read_excel(file_path)
                    name = file_name + '-' + last_dir
                    # 将数据存储到字典中
                    # 筛选数据 选择 DataFrame data 的最后 6 行，并从中提取第 2 列到倒数第 4 列（不包括倒数第 4 列）的所有列
                    selected_rows = data.tail(6).iloc[:, 1:-4]
                    # 获取列名
                    column_name = selected_rows.columns[0]
                    # 删除包含空值的行
                    selected_rows = selected_rows.dropna(subset=[column_name])
                    df = pd.DataFrame(selected_rows.values)
                    df.columns = range(df.shape[1])  # 重新分配列名为整数索引
                    df.columns = [''] * len(df.columns)
                    self.original_dict[name] = df

    def data_transform(self):
        for key, value in self.original_dict.items():
            # 获取数据
            self.transform_data[key] = {
                # key.split('-')[0],
                'name':key[:4],
                's':float(value.iloc[0, 6]),
                'z':float(value.iloc[0, 5]),

            }


# example = MeasurementData(
#     'E:/2024/金川水电站补充测量/大渡河金川水电站五甲村三四组对外道路控制点补测项目三角高程/三角高程原始数据 - 副本')
# example.process_directory()
# print(example.transform_data)
