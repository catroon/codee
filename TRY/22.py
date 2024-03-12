import os  
import pandas as pd  
  
# 设定源文件夹路径  
source_folder = "C:\\Users\\HUIKE\\Desktop\\333"  
  
# 获取源文件夹中所有的.csv文件  
csv_files = [f for f in os.listdir(source_folder) if f.endswith('.csv')]  
  
# 初始化一个空的列表来存储所有的DataFrames  
all_data = []  
  
# 遍历CSV文件并尝试读取它们  
for csv_file in csv_files:  
    file_path = os.path.join(source_folder, csv_file)  
    try:  
        # 读取CSV文件到DataFrame  
        df = pd.read_csv(file_path)  
        # 将DataFrame添加到列表中  
        all_data.append(df)  
        print(f"Read file successfully: {file_path}")  
    except Exception as e:  
        print(f"Error reading file {file_path}: {e}")  
        # 可以选择继续读取其他文件，或者根据错误类型决定是否退出  
  
# 检查是否成功读取了至少一个文件  
if not all_data:  
    print("No CSV files were successfully read.")  
else:  
    # 横向合并所有的DataFrames  
    try:  
        merged_data = pd.concat(all_data, axis=1)  
    except ValueError as e:  
        print("Error merging the dataframes:", e)  
    else:  
        # 输出合并后的CSV文件  
        output_file = "C:\\Users\\HUIKE\\Desktop\\merged_data.csv"  
        merged_data.to_csv(output_file, index=False)  
        print(f"All CSV files have been horizontally merged into '{output_file}'.")