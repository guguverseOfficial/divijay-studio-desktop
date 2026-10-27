import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import os
import sys
import json
import random
import logging
import subprocess

# === НАСТРОЙКА ОКРУЖЕНИЯ (Для PyInstaller) ===
# Определяем, запущены мы как EXE или как обычный скрипт
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS # Временная папка, куда PyInstaller распаковывает файлы
    EXE_DIR = os.path.dirname(sys.executable) # Папка, где лежит сам EXE
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    EXE_DIR = BASE_DIR

# Создаем папки для сохранений в папке с EXE (чтобы они не терялись)
os.makedirs(os.path.join(EXE_DIR, 'logs'), exist_ok=True)
for folder in ['output/spritesheets', 'output/charts', 'output/icons', 'output/audio']:
    os.makedirs(os.path.join(EXE_DIR, folder), exist_ok=True)

# Настройка логов
logging.basicConfig(
    filename=os.path.join(EXE_DIR, 'logs', 'studio.log'), 
    level=logging.INFO, 
    format='%(asctime)s - %(message)s'
)

# Настройки внешнего вида
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# ==========================================
# ЛОГИКА (МОЗГИ ПРОГРАММЫ)
# ==========================================

def generate_xml(xml_data, output_path):
    xml_string = '<?xml version="1.0" encoding="utf-8"?>\n<TextureAtlas imagePath="spritesheet.png">\n'
    for item in xml_data:
        xml_string += f'    <SubTexture name="{item["name"]}" x="{item["x"]}" y="{item["y"]}" width="{item["width"]}" height="{item["height"]}"/>\n'
    xml_string += '</TextureAtlas>'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(xml_string)

def process_spritesheet(folder_path, columns=4):
    try:
        images = [f for f in os.listdir(folder_path) if f.lower().endswith('.png')]
        images.sort()
        if not images: return False, "В папке нет PNG файлов!"

        loaded_images = []
        max_w, max_h = 0, 0
        
        for img_name in images:
            img = Image.open(os.path.join(folder_path, img_name)).convert("RGBA")
            loaded_images.append((img_name.replace('.png', ''), img))
            max_w = max(max_w, img.width)
            max_h = max(max_h, img.height)

        rows = (len(loaded_images) + columns - 1) // columns
        sheet_w = max_w * columns
        sheet_h = max_h * rows

        spritesheet = Image.new('RGBA', (sheet_w, sheet_h), (0, 0, 0, 0))
        xml_data = []

        for i, (name, img) in enumerate(loaded_images):
            col = i % columns
            row = i // columns
            x = col * max_w
            y = row * max_h
            
            spritesheet.paste(img, (x, y))
            xml_data.append({"name": name, "x": x, "y": y, "width": img.width, "height": img.height})

        out_png = os.path.join(EXE_DIR, 'output', 'spritesheets', 'spritesheet.png')
        out_xml = os.path.join(EXE_DIR, 'output', 'spritesheets', 'spritesheet.xml')
        
        spritesheet.save(out_png)
        generate_xml(xml_data, out_xml)
        return True, f"Успешно собрано {len(loaded_images)} картинок!\nСохранено в папку output."
    except Exception as e:
        logging.error(str(e))
        return False, str(e)

def process_icon(image_path, size):
    try:
        img = Image.open(image_path).convert("RGBA")
        min_dim = min(img.width, img.height)
        left = (img.width - min_dim) / 2
        top = (img.height - min_dim) / 2
        right = (img.width + min_dim) / 2
        bottom = (img.height + min_dim) / 2
        
        img_cropped = img.crop((left, top, right, bottom))
        img_resized = img_cropped.resize((size, size), Image.Resampling.LANCZOS)
        
        out_path = os.path.join(EXE_DIR, 'output', 'icons', 'icon.png')
        img_resized.save(out_path)
        return True, f"Иконка {size}x{size} сохранена в output."
    except Exception as e:
        logging.error(str(e))
        return False, str(e)

def process_chart(bpm, duration):
    try:
        ms_per_beat = 60000 / bpm
        ms_per_section = ms_per_beat * 4
        num_sections = int((duration * 1000) / ms_per_section) + 1
        sections = []
        
        for i in range(num_sections):
            notes = []
            for j in range(4):
                if random.random() > 0.3:
                    notes.append([int(j * ms_per_beat), random.randint(0, 3), 0])
            sections.append({
                "sectionNotes": notes, "bpm": bpm, "changeBPM": False,
                "mustHitSection": True, "altAnim": False, "gfSection": False, "sectionBeats": 4
            })

        chart_data = {
            "song": {
                "song": "Auto Generated", "bpm": bpm, "speed": 1.0,
                "player1": "bf", "player2": "dad", "gfVersion": "gf",
                "stage": "stage", "needsVoices": True, "notes": sections
            }
        }
        
        out_path = os.path.join(EXE_DIR, 'output', 'charts', 'chart.json')
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(chart_data, f, indent=4)
        return True, f"Чарт создан! Секций: {num_sections}\nСохранено в output."
    except Exception as e:
        logging.error(str(e))
        return False, str(e)

def convert_audio(input_file):
    try:
        output_file = os.path.join(EXE_DIR, 'output', 'audio', 'converted.ogg')
        
        # Ищем ffmpeg.exe. Сначала во временной папке PyInstaller, потом рядом с EXE/скриптом.
        possible_paths = [
            os.path.join(BASE_DIR, 'ffmpeg.exe'),
            os.path.join(EXE_DIR, 'ffmpeg.exe')
        ]
        
        ffmpeg_path = None
        for path in possible_paths:
            if os.path.exists(path):
                ffmpeg_path = path
                break
                
        if not ffmpeg_path:
            return False, "Ошибка: ffmpeg.exe не найден!\nПоложите его в папку с программой."
            
        cmd = [ffmpeg_path, '-y', '-i', input_file, output_file]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True, "Конвертация успешна! Файл в output/audio/"
    except subprocess.CalledProcessError:
        return False, "Ошибка FFmpeg. Возможно, файл поврежден."
    except Exception as e:
        logging.error(str(e))
        return False, str(e)

# ==========================================
# ИНТЕРФЕЙС (ВКЛАДКИ)
# ==========================================

class SpritesTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.folder_path = None
        
        self.path_entry = ctk.CTkEntry(self, placeholder_text="Путь к папке с PNG...", width=450)
        self.path_entry.pack(pady=15)
        ctk.CTkButton(self, text="Выбрать папку", command=self.select).pack(pady=5)
        
        self.col_frame = ctk.CTkFrame(self); self.col_frame.pack(pady=10)
        ctk.CTkLabel(self.col_frame, text="Колонок:").pack(side="left", padx=5)
        self.col_entry = ctk.CTkEntry(self.col_frame, width=50)
        self.col_entry.insert(0, "4")
        self.col_entry.pack(side="left")

        self.btn = ctk.CTkButton(self, text="СОБРАТЬ СПРАЙТ-ЛИСТ", fg_color="#e67e22", state="disabled", command=self.run)
        self.btn.pack(pady=15)
        self.status = ctk.CTkLabel(self, text="Ожидание...", text_color="gray")
        self.status.pack(pady=10)

    def select(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.path_entry.delete(0, 'end')
            self.path_entry.insert(0, self.folder_path)
            self.btn.configure(state="normal")
            self.status.configure(text="Папка выбрана.", text_color="#2ecc71")

    def run(self):
        self.status.configure(text="Собираю...", text_color="yellow")
        self.update()
        try:
            cols = int(self.col_entry.get())
        except:
            cols = 4
            
        success, msg = process_spritesheet(self.folder_path, cols)
        self.status.configure(text="УСПЕХ!" if success else "ОШИБКА!", text_color="#2ecc71" if success else "#e74c3c")
        (messagebox.showinfo if success else messagebox.showerror)("Результат", msg)

class ChartsTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        frame1 = ctk.CTkFrame(self); frame1.pack(pady=10)
        ctk.CTkLabel(frame1, text="BPM:").pack(side="left", padx=5)
        self.bpm = ctk.CTkEntry(frame1, width=100); self.bpm.insert(0, "150"); self.bpm.pack(side="left")
        
        frame2 = ctk.CTkFrame(self); frame2.pack(pady=10)
        ctk.CTkLabel(frame2, text="Длительность (сек):").pack(side="left", padx=5)
        self.dur = ctk.CTkEntry(frame2, width=100); self.dur.insert(0, "60"); self.dur.pack(side="left")
        
        ctk.CTkButton(self, text="СОЗДАТЬ ЧАРТ", fg_color="#e67e22", command=self.run).pack(pady=20)
        self.status = ctk.CTkLabel(self, text="Ожидание...", text_color="gray")
        self.status.pack(pady=10)

    def run(self):
        try:
            self.status.configure(text="Генерирую...", text_color="yellow")
            self.update()
            success, msg = process_chart(int(self.bpm.get()), int(self.dur.get()))
            self.status.configure(text="УСПЕХ!" if success else "ОШИБКА!", text_color="#2ecc71" if success else "#e74c3c")
            (messagebox.showinfo if success else messagebox.showerror)("Результат", msg)
        except ValueError:
            messagebox.showerror("Ошибка", "Введи числа в поля BPM и Длительность!")

class IconsTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.img_path = None
        
        self.path_entry = ctk.CTkEntry(self, placeholder_text="Путь к картинке...", width=450)
        self.path_entry.pack(pady=15)
        ctk.CTkButton(self, text="Выбрать PNG", command=self.select).pack(pady=5)
        
        frame = ctk.CTkFrame(self); frame.pack(pady=15)
        ctk.CTkLabel(frame, text="Размер (px):").pack(side="left", padx=5)
        self.size = ctk.CTkEntry(frame, width=100); self.size.insert(0, "150"); self.size.pack(side="left")
        
        self.btn = ctk.CTkButton(self, text="СОЗДАТЬ ИКОНКУ", fg_color="#e67e22", state="disabled", command=self.run)
        self.btn.pack(pady=15)
        self.status = ctk.CTkLabel(self, text="Ожидание...", text_color="gray")
        self.status.pack(pady=10)

    def select(self):
        self.img_path = filedialog.askopenfilename(filetypes=[("PNG", "*.png")])
        if self.img_path:
            self.path_entry.delete(0, 'end')
            self.path_entry.insert(0, self.img_path)
            self.btn.configure(state="normal")
            self.status.configure(text="Готов к генерации.", text_color="#2ecc71")

    def run(self):
        self.status.configure(text="Генерирую...", text_color="yellow")
        self.update()
        try:
            sz = int(self.size.get())
        except:
            sz = 150
        success, msg = process_icon(self.img_path, sz)
        self.status.configure(text="УСПЕХ!" if success else "ОШИБКА!", text_color="#2ecc71" if success else "#e74c3c")
        (messagebox.showinfo if success else messagebox.showerror)("Результат", msg)

class AudioTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.audio_path = None
        
        self.path_entry = ctk.CTkEntry(self, placeholder_text="Путь к MP3...", width=450)
        self.path_entry.pack(pady=20)
        ctk.CTkButton(self, text="Выбрать MP3", command=self.select).pack(pady=5)
        
        self.btn = ctk.CTkButton(self, text="КОНВЕРТИРОВАТЬ В OGG", fg_color="#e67e22", state="disabled", command=self.run)
        self.btn.pack(pady=30)
        self.status = ctk.CTkLabel(self, text="Ожидание...", text_color="gray")
        self.status.pack(pady=10)

    def select(self):
        self.audio_path = filedialog.askopenfilename(filetypes=[("MP3", "*.mp3")])
        if self.audio_path:
            self.path_entry.delete(0, 'end')
            self.path_entry.insert(0, self.audio_path)
            self.btn.configure(state="normal")
            self.status.configure(text="Готов к конвертации.", text_color="#2ecc71")

    def run(self):
        self.status.configure(text="Конвертирую...", text_color="yellow")
        self.update()
        success, msg = convert_audio(self.audio_path)
        self.status.configure(text="УСПЕХ!" if success else "ОШИБКА!", text_color="#2ecc71" if success else "#e74c3c")
        (messagebox.showinfo if success else messagebox.showerror)("Результат", msg)

# ==========================================
# ГЛАВНОЕ ОКНО
# ==========================================

class DivijayStudio(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Divijay Studio Desktop 2.0 | Guguverse Studios")
        self.geometry("900x700")
        self.minsize(800, 600)

        # Заголовок
        ctk.CTkLabel(self, text="GUGUVERSE STUDIOS", font=("Arial Black", 24), text_color="#2ecc71").pack(pady=(15, 0))
        ctk.CTkLabel(self, text="Divijay Studio Desktop (Полная версия)", font=("Arial", 14), text_color="gray").pack(pady=(0, 15))

        # Вкладки
        tabs = ctk.CTkTabview(self)
        tabs.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        SpritesTab(tabs.add("Спрайт-листы")).pack(fill="both", expand=True)
        ChartsTab(tabs.add("Генератор чартов")).pack(fill="both", expand=True)
        IconsTab(tabs.add("Генератор иконок")).pack(fill="both", expand=True)
        AudioTab(tabs.add("Конвертер аудио")).pack(fill="both", expand=True)

if __name__ == "__main__":
    try:
        app = DivijayStudio()
        app.mainloop()
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
        messagebox.showerror("Критическая ошибка", str(e))