import logging
from dotenv import load_dotenv, dotenv_values
import os
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
load_dotenv()

logging_initialized = False

def setup_logging():
    global logging_initialized
    if not logging_initialized:
        print("LOG_LEVEL from env:", os.getenv('LOG_LEVEL'))
        log_level = os.getenv('LOG_LEVEL', 'DEBUG').upper()
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'app-pe-ai-assistant.log')

        logging.basicConfig(level=getattr(logging, log_level),
                            handlers=[
                                logging.FileHandler(log_file, mode='w'),
                                logging.StreamHandler()
                            ],
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logging_initialized = True

def reload_env_and_logging():
    # Загрузка новых значений из .env файла
    env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')  # Путь к вашему .env файлу
    new_env = dotenv_values(env_path)
    
    # Обновление переменных окружения
    os.environ.update(new_env)
    
    # Переинициализация логирования
    setup_logging()

# Вызов функции для перезагрузки
reload_env_and_logging()
