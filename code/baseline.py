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