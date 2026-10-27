def generate_xml(xml_data, output_path):
    xml_string = '<?xml version="1.0" encoding="utf-8"?>\n<TextureAtlas imagePath="spritesheet.png">\n'
    
    for item in xml_data:
        xml_string += f'    <SubTexture name="{item["name"]}" x="{item["x"]}" y="{item["y"]}" width="{item["width"]}" height="{item["height"]}"/>\n'
        
    xml_string += '</TextureAtlas>'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(xml_string)