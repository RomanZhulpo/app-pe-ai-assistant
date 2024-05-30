import logging
from dotenv import load_dotenv
import os

load_dotenv()

def setup_logging():
    # Установка значения по умолчанию для log_level, если переменная окружения не задана
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()  # 'INFO' как значение по умолчанию
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'app-pe-ai-assistant.log')

    logging.basicConfig(level=getattr(logging, log_level),
                        handlers=[
                            logging.FileHandler(log_file, mode='w'),
                            logging.StreamHandler()
                        ],
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')