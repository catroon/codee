import numpy as np
import csv
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog, messagebox
import rampy

def read_csv_file(file_path):
    data = []
    with open(file_path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader, None)  # 跳过标题行
        for row in csv_reader:
            row_values = [float(val) for val in row]  # 将每行转换为浮点数
            data.append(row_values)
    return np.array(data)

def process_data(csv_file_path, roi, polynomial_order):
    data = read_csv_file(csv_file_path)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for i in range(0, data.shape[1], 2):
        x = data[:, i]
        y = data[:, i+1]

        # 应用基线校正
        ycalc_poly, base_poly = rampy.baseline(x, y, roi, 'poly', polynomial_order=polynomial_order)

        # 绘制原始数据和校正后的数据
        ax.plot(x, y, label="Original Data")
        ax.plot(x, base_poly, "-", label=f"Data {i//2 + 1}")

    # 设置图形标题和标签
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.legend()
    ax.grid(True)

    return fig, data

def browse_file():
    file_path = filedialog.askopenfilename()
    entry.delete(0, tk.END)
    entry.insert(0, file_path)

def save_csv(data):
    csv_file_path = filedialog.asksaveasfilename(defaultextension=".csv")
    if csv_file_path:
        np.savetxt(csv_file_path, data, delimiter=",")
        messagebox.showinfo("Save CSV", "CSV file saved successfully.")

def save_svg(fig):
    svg_file_path = filedialog.asksaveasfilename(defaultextension=".svg")
    if svg_file_path:
        fig.savefig(svg_file_path, format='svg')
        messagebox.showinfo("Save SVG", "SVG file saved successfully.")

def save_data(data):
    file_path = filedialog.asksaveasfilename(defaultextension=".txt")
    if file_path:
        np.savetxt(file_path, data, delimiter=",")
        messagebox.showinfo("Save Data", "Data saved successfully.")

def plot_data():
    csv_file_path = entry.get()
    roi_text = roi_entry.get("1.0", "end-1c")
    roi = parse_roi(roi_text)
    polynomial_order = int(order_entry.get())
    fig, data = process_data(csv_file_path, roi, polynomial_order)
    
    # 创建一个新的框架用于放置图形和数据保存框
    plot_frame = tk.Frame(root)
    plot_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    # 在新的框架中绘制图形
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
    
    # 创建一个文本框用于显示数据
    data_text = tk.Text(plot_frame, width=50, height=10)
    data_text.pack(side=tk.LEFT, padx=5, pady=5)
    data_text.insert(tk.END, np.array2string(data))
    
    # 创建保存数据的按钮
    save_data_button = tk.Button(plot_frame, text="Save Data", command=lambda: save_data(data))
    save_data_button.pack(side=tk.BOTTOM, padx=5, pady=5)

def parse_roi(roi_text):
    roi = []
    lines = roi_text.split("\n")
    for line in lines:
        line = line.strip()
        if line:
            try:
                start, end = map(int, line.split(","))
                roi.append([start, end])
            except ValueError:
                print("Invalid ROI format")
    return np.array(roi)

# 创建GUI窗口
root = tk.Tk()
root.title("Baseline Correction GUI")

# 创建文件路径输入框和浏览按钮
entry = tk.Entry(root, width=50)
entry.pack(side=tk.TOP, padx=5, pady=5)
browse_button = tk.Button(root, text="Browse", command=browse_file)
browse_button.pack(side=tk.TOP, padx=5, pady=5)

# 创建ROI输入框
roi_label = tk.Label(root, text="ROI:")
roi_label.pack(side=tk.TOP, padx=5, pady=5)
roi_entry = tk.Text(root, width=50, height=2)
roi_entry.pack(side=tk.TOP, padx=5, pady=5)

# 创建多项式阶数输入框
order_label = tk.Label(root, text="Polynomial Order:")
order_label.pack(side=tk.TOP, padx=5, pady=5)
order_entry = tk.Entry(root, width=5)
order_entry.pack(side=tk.TOP, padx=5, pady=5)

# 创建绘图按钮
plot_button = tk.Button(root, text="Plot Data", command=plot_data)
plot_button.pack(side=tk.TOP, padx=5, pady=5)

# 运行GUI
root.mainloop()
