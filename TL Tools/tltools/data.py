import os

import pandas as pd


def process_directory(directory):
    data_dict = {}  # 创建一个空字典来存储数据

    # 使用os.walk遍历目录下的所有文件和子目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.xls'):
                # 获取文件的完整路径
                file_path = os.path.join(root, file)
                # 读取表格文件
                data = pd.read_excel(file_path)
                data.to_excel(file_path.replace(".xls", "_temp.xlsx"), index=False)
                # 读取表格文件
    for root, dirs, files in os.walk(directory):
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
                # 筛选数据
                last_eight_rows = data.tail(6).iloc[:, 1:-4]
                column_name = last_eight_rows.columns[0]
                last_eight_rows = last_eight_rows.dropna(subset=[column_name])
                df = pd.DataFrame(last_eight_rows.values)
                df.columns = range(df.shape[1])  # 重新分配列名为整数索引
                df.columns = [''] * len(df.columns)
                data_dict[name] = df
    return data_dict


if __name__ == '__main__':
    process_directory(
        'E:/2024/金川水电站补充测量/大渡河金川水电站五甲村三四组对外道路控制点补测项目三角高程/三角高程原始数据 - 副本')
