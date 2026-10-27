import customtkinter as ctk
from src.ui.tab_sprites import SpritesTab
from src.utils.file_manager import create_output_folders

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class DivijayStudioApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Divijay Studio Desktop | Guguverse Studios")
        self.geometry("800x600")
        self.minsize(600, 400)
        
        # Создаем папки для сохранений
        create_output_folders()

        # Заголовок
        self.label_title = ctk.CTkLabel(self, text="GUGUVERSE STUDIOS", font=("Arial Black", 24), text_color="#2ecc71")
        self.label_title.pack(pady=(15, 0))
        
        self.label_sub = ctk.CTkLabel(self, text="Divijay Studio Desktop", font=("Arial", 14), text_color="gray")
        self.label_sub.pack(pady=(0, 15))

        # Вкладки
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.tab_sprites = self.tabview.add("Генератор спрайтов")
        self.tab_charts = self.tabview.add("Генератор чартов")
        self.tab_icons = self.tabview.add("Генератор иконок")

        # Подключаем интерфейс спрайтов
        self.sprites_ui = SpritesTab(self.tab_sprites)
        self.sprites_ui.pack(fill="both", expand=True)
        
        # Заглушки для других вкладок
        ctk.CTkLabel(self.tab_charts, text="Генератор чартов (в разработке)").pack(pady=50)
        ctk.CTkLabel(self.tab_icons, text="Генератор иконок (в разработке)").pack(pady=50)