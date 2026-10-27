from PIL import Image
import os
from src.core.xml_generator import generate_xml

def create_spritesheet(folder_path, columns=4):
    try:
        # 1. Получаем все PNG из папки
        images = [f for f in os.listdir(folder_path) if f.lower().endswith('.png')]
        images.sort()
        
        if not images:
            return False, "В папке нет PNG файлов!"

        loaded_images = []
        max_w, max_h = 0, 0
        
        # 2. Загружаем и ищем максимальный размер
        for img_name in images:
            img = Image.open(os.path.join(folder_path, img_name)).convert("RGBA")
            loaded_images.append((img_name.replace('.png', ''), img))
            max_w = max(max_w, img.width)
            max_h = max(max_h, img.height)

        # 3. Вычисляем размеры листа
        rows = (len(loaded_images) + columns - 1) // columns
        sheet_w = max_w * columns
        sheet_h = max_h * rows

        # 4. Создаем пустой холст (прозрачный)
        spritesheet = Image.new('RGBA', (sheet_w, sheet_h), (0, 0, 0, 0))
        xml_data = []

        # 5. Вставляем картинки
        for i, (name, img) in enumerate(loaded_images):
            col = i % columns
            row = i // columns
            x = col * max_w
            y = row * max_h
            
            spritesheet.paste(img, (x, y))
            
            xml_data.append({
                "name": name,
                "x": x, "y": y, 
                "width": img.width, "height": img.height
            })

        # 6. Сохраняем PNG
        out_png = 'output/spritesheets/spritesheet.png'
        spritesheet.save(out_png)
        
        # 7. Генерируем XML
        generate_xml(xml_data, 'output/spritesheets/spritesheet.xml')
        
        return True, f"Успешно собрано {len(loaded_images)} картинок!\nСохранено в output/spritesheets/"
    
    except Exception as e:
        return False, str(e)
 