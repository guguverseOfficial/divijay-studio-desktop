import customtkinter as ctk

class ChartsTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="Тут скоро будет генератор чартов\n(Как на сайте, только быстрее!)", font=("Arial", 16)).pack(pady=50)