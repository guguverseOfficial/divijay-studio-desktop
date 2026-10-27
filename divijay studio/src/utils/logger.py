import logging
import os

def setup_logger():
    # Создаем папку для логов, если ее нет
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    logging.basicConfig(
        filename='logs/studio.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        encoding='utf-8'
    )
    logging.info("=== Запуск Divijay Studio ===")