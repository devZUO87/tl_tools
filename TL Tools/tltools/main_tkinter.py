from tkinter import *

from data_oop import MeasurementData


# Table class


class Table:
    # Initialize a constructor
    def __init__(self, gui):
        # total_rows = len(employee_list)
        # total_columns = len(employee_list[list(employee_list.keys())[0]])

        # 创建表格
        for i, (key, value) in enumerate(employee_list.items()):
            # 插入文件名
            self.entry = Entry(gui, width=20, fg="blue", font=("Arial", 16, ""))
            self.entry.grid(row=i, column=0)
            self.entry.insert(END, key)

            # 插入其他数据
            for j, (k, v) in enumerate(value.items()):
                self.entry = Entry(gui, width=20, fg="blue", font=("Arial", 16, ""))
                self.entry.grid(row=i, column=j + 1)
                self.entry.insert(END, v)


example = MeasurementData(
    'D:/tl_tools/data/原始数据/test/YQ0311')
# take the data
employee_list = example.transform_data


# find total number of rows and
# columns in list


gui1 = Tk()
table = Table(gui1)
gui1.mainloop()
