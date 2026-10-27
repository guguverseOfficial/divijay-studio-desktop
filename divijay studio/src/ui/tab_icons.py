import customtkinter as ctk

class IconsTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="Тут скоро будет генератор иконок\n(Для персонажей FNF)", font=("Arial", 16)).pack(pady=50)