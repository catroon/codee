import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def adjust_data(file_path, increment):
    data = pd.read_csv(file_path)

    # 调整数据使后一组数据高于前一组数据
    for i in range(1, len(data.columns), 2):
        data.iloc[:, i] = data.iloc[:, i] + i * increment

    return data

def plot_line_chart(data, x_min, x_max, save_csv_path, save_svg_path):
    # 绘制折线图
    plt.figure(figsize=(10, 6))
    for i in range(0, len(data.columns), 2):
        plt.plot(data.iloc[:, i], data.iloc[:, i + 1], label=f"Line {i//2+1}")

    plt.xlabel("X Axis")
    plt.ylabel("Y Axis")
    plt.title("Line Chart")
    plt.legend()
    plt.grid(True)

    # 用户自定义X轴范围
    plt.xlim(x_min, x_max)

    # 保存CSV文件
    if save_csv_path:
        data_to_save = data.loc[(data.iloc[:, 0] >= x_min) & (data.iloc[:, 0] <= x_max)]
        data_to_save.to_csv(save_csv_path, index=False)
        messagebox.showinfo("Success", f"CSV file saved successfully: {save_csv_path}")

    # 保存矢量图
    if save_svg_path:
        plt.savefig(save_svg_path, format="svg")
        messagebox.showinfo("Success", f"SVG file saved successfully: {save_svg_path}")

    plt.show()

def plot_and_save():
    # 读取文件
    file_path = file_path_entry.get()
    increment = float(increment_entry.get())
    x_min = float(x_min_entry.get())
    x_max = float(x_max_entry.get())

    # 调整数据
    data = adjust_data(file_path, increment)

    # 获取用户选择的保存路径
    save_csv_path = csv_file_path_entry.get()
    save_svg_path = svg_file_path_entry.get()

    # 绘制折线图并保存
    plot_line_chart(data, x_min, x_max, save_csv_path, save_svg_path)

# 创建GUI窗口
root = tk.Tk()
root.title("Line Chart Generator")

# 添加选择CSV文件按钮
file_path_label = tk.Label(root, text="Select CSV File:")
file_path_label.pack()

file_path_entry = tk.Entry(root, width=50)
file_path_entry.pack()

browse_button = tk.Button(root, text="Browse", command=lambda: file_path_entry.insert(tk.END, filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])) )
browse_button.pack(pady=5)

# 添加文本框和标签用于输入高度增量
increment_label = tk.Label(root, text="Increment:")
increment_label.pack()
increment_entry = tk.Entry(root)
increment_entry.pack()

# 添加文本框和标签用于输入X轴范围
x_range_label = tk.Label(root, text="X Axis Range:")
x_range_label.pack()

x_min_entry = tk.Entry(root)
x_min_entry.insert(tk.END, "400")
x_min_entry.pack()

x_max_entry = tk.Entry(root)
x_max_entry.insert(tk.END, "4000")
x_max_entry.pack()

# 添加选择保存CSV文件的文件框
csv_file_path_label = tk.Label(root, text="Select CSV Save Path (Optional):")
csv_file_path_label.pack()

csv_file_path_entry = tk.Entry(root, width=50)
csv_file_path_entry.pack()

csv_browse_button = tk.Button(root, text="Browse", command=lambda: csv_file_path_entry.insert(tk.END, filedialog.asksaveasfilename(defaultextension=".csv")) )
csv_browse_button.pack(pady=5)

# 添加选择保存SVG文件的文件框
svg_file_path_label = tk.Label(root, text="Select SVG Save Path (Optional):")
svg_file_path_label.pack()

svg_file_path_entry = tk.Entry(root, width=50)
svg_file_path_entry.pack()

svg_browse_button = tk.Button(root, text="Browse", command=lambda: svg_file_path_entry.insert(tk.END, filedialog.asksaveasfilename(defaultextension=".svg")) )
svg_browse_button.pack(pady=5)

# 添加按钮用于绘制折线图并保存
plot_button = tk.Button(root, text="Plot and Save", command=plot_and_save)
plot_button.pack(pady=10)

# 运行GUI
root.mainloop()
