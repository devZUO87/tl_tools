import ipywidgets as widgets
import pandas as pd
from IPython.display import display

import tltools.data as data

directory = 'E:/2024/金川水电站补充测量/大渡河金川水电站五甲村三四组对外道路控制点补测项目三角高程/三角高程原始数据 - 副本'
data_dict = data.process_directory(directory)

# 初始化结果列表
results = []

# 遍历 data_dict 中的每个 DataFrame
for key, df in data_dict.items():
    for index, row in df.iterrows():
        # 提取第 5 列和第 6 列的值
        s = row.iloc[5]
        z = row.iloc[6]
        results.append([key, index, s, z])

# 创建结果 DataFrame
results_df = pd.DataFrame(results, columns=['key', 'Index', 's', 'z'])

# 创建输出部件
output = widgets.Output()


def show_table(df):
    with output:
        output.clear_output()
        display(df)


show_table(results_df)

# 创建交互式表格
sorted_df = results_df.copy()
table = widgets.VBox([
    widgets.HTML(value=sorted_df.to_html(index=False)),
    widgets.HBox([
        widgets.Label('Sort by:'),
        widgets.Dropdown(options=sorted_df.columns, value='s', description='Column:'),
        widgets.Button(description='Sort')
    ])
])


def on_sort_button_clicked(b):
    global sorted_df
    col = table.children[1].children[1].value
    sorted_df = sorted_df.sort_values(by=col)
    table.children[0].value = sorted_df.to_html(index=False)
    show_table(sorted_df)


table.children[1].children[2].on_click(on_sort_button_clicked)

display(table, output)
