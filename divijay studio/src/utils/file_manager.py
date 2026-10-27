import os
from tkinter import messagebox

def create_output_folders():
    folders = ['output/spritesheets', 'output/charts', 'output/icons']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

def check_folder(folder_path):
    if not folder_path or not os.path.exists(folder_path):
        messagebox.showerror("Ошибка", "Папка не выбрана или не существует!")
        return False
    return True