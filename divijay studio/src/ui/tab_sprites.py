import customtkinter as ctk
from tkinter import filedialog, messagebox
from src.core.image_processor import create_spritesheet
from src.utils.file_manager import check_folder
import logging

class SpritesTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.folder_path = None

        # Поле для пути
        self.path_entry = ctk.CTkEntry(self, placeholder_text="Путь к папке с PNG...", width=400)
        self.path_entry.pack(pady=20)

        # Кнопка выбора
        self.btn_select = ctk.CTkButton(self, text="Выбрать папку", command=self.select_folder)
        self.btn_select.pack(pady=5)

        # Кнопка генерации
        self.btn_generate = ctk.CTkButton(self, text="СОБРАТЬ СПРАЙТ-ЛИСТ", fg_color="#e67e22", hover_color="#d35400", state="disabled", command=self.generate)
        self.btn_generate.pack(pady=30)

        # Статус
        self.status_label = ctk.CTkLabel(self, text="Ожидание...", text_color="gray")
        self.status_label.pack(pady=10)

    def select_folder(self):
        self.folder_path = filedialog.askdirectory(title="Выбери папку с PNG картинками")
        if self.folder_path:
            self.path_entry.delete(0, 'end')
            self.path_entry.insert(0, self.folder_path)
            self.btn_generate.configure(state="normal")
            self.status_label.configure(text="Папка выбрана. Готов к сборке.", text_color="#2ecc71")

    def generate(self):
        if not check_folder(self.folder_path):
            return
            
        self.status_label.configure(text="Собираю спрайт-лист... Пожалуйста, подожди.", text_color="yellow")
        self.update() # Принудительно обновляем интерфейс
        
        success, message = create_spritesheet(self.folder_path, columns=4)
        
        if success:
            self.status_label.configure(text="УСПЕХ! Файлы сохранены в output/", text_color="#2ecc71")
            messagebox.showinfo("Готово", message)
            logging.info(message)
        else:
            self.status_label.configure(text="Ошибка при сборке!", text_color="#e74c3c")
            messagebox.showerror("Ошибка", message)
            logging.error(message)