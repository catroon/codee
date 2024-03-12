import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

def merge_csv_files(folder_path, save_path):
    merged_data = pd.DataFrame()
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(folder_path, filename)
            data = pd.read_csv(file_path)
            title = os.path.splitext(filename)[0]
            merged_data[title + '_x'] = data.iloc[:, 0]
            merged_data[title + '_y'] = data.iloc[:, 1]
    return merged_data, save_path

def browse_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder_path)

def browse_save_location():
    save_path = filedialog.asksaveasfilename(defaultextension=".csv")
    if save_path:
        save_entry.delete(0, tk.END)
        save_entry.insert(0, save_path)

def merge_and_save():
    folder_path = folder_entry.get()
    save_path = save_entry.get()
    if folder_path and save_path:
        merged_data, _ = merge_csv_files(folder_path, save_path)
        merged_data.to_csv(save_path, index=False)
        messagebox.showinfo("Success", "CSV files merged successfully and saved as " + save_path)

# 创建GUI窗口
root = tk.Tk()
root.title("CSV File Merger")

# 添加标签、文本框和按钮
folder_label = tk.Label(root, text="Folder Path:")
folder_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

folder_entry = tk.Entry(root, width=50)
folder_entry.grid(row=0, column=1, padx=10, pady=5)

browse_folder_button = tk.Button(root, text="Browse", command=browse_folder)
browse_folder_button.grid(row=0, column=2, padx=5, pady=5)

save_label = tk.Label(root, text="Save As:")
save_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

save_entry = tk.Entry(root, width=50)
save_entry.grid(row=1, column=1, padx=10, pady=5)

browse_save_button = tk.Button(root, text="Browse", command=browse_save_location)
browse_save_button.grid(row=1, column=2, padx=5, pady=5)

merge_button = tk.Button(root, text="Merge and Save", command=merge_and_save)
merge_button.grid(row=2, column=1, padx=10, pady=20)

# 运行GUI
root.mainloop()
