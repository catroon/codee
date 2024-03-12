import numpy as np
import csv
from matplotlib import pyplot as plt
import rampy

def read_csv_file(file_path):
    x_values = []
    y_values = []
    with open(file_path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader, None)  # 跳过标题行
        for row in csv_reader:
            for i in range(0, len(row), 2):
                x_values.append(float(row[i]))
                y_values.append(float(row[i + 1]))
    return np.array(x_values), np.array(y_values)

# 从CSV文件读取数据
csv_file_path = r'C:\Users\HUIKE\Desktop\date\1.csv'  # 假设CSV文件路径为这个
x, y = read_csv_file(csv_file_path)

# 定义感兴趣的区域（ROI）
roi = np.array([[500,600],[900,1200],[1900,2200],[2700,3200],[3700,4000]])

# 应用基线校正
ycalc_poly, base_poly = rampy.baseline(x, y, roi, 'poly', polynomial_order=11)

# 绘制原始数据和校正后的数据
plt.figure(dpi=150)
plt.plot(x, y, label="Original Data")
plt.plot(x, base_poly, "-", color="grey", label="Polynomial Baseline")
plt.xlabel("X")
plt.ylabel("Y")
plt.legend()
plt.grid(True)
plt.show()
