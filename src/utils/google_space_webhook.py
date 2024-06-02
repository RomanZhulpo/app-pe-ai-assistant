import os
import requests
import json
import sys
from pathlib import Path
import logging

project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from src.config.logging_config import setup_logging  # Убедитесь, что путь импорта корректен

# Настройка логирования
setup_logging()
logger = logging.getLogger(__name__)  # Создание логгера для модуля

class GoogleChatWebhook:
    def __init__(self, webhook_url):
        self.url = webhook_url

    def send_message(self, message):
        # Убедитесь, что message является строкой
        if not isinstance(message, str):
            logger.error("Отправляемое сообщение должно быть строкой")
            return None

        app_message = {"text": message}
        try:
            response = requests.post(self.url, json=app_message)
            logger.debug(f"Отправляемое сообщение: {json.dumps(app_message)}")
            logger.debug(f"Ответ сервера: {response.status_code}, {response.text}")
            
            if response.status_code != 200:
                logger.error(f"Ошибка отправки сообщения: {response.text}")
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при отправке сообщения: {e}")
            return None

if __name__ == "__main__":
    webhook_url = os.getenv("WEBHOOK_URL")
    webhook = GoogleChatWebhook(webhook_url)
    response = webhook.send_message("Привет от Python скрипта!")
    if response:
        logger.info(f"Статус ответа: {response.status_code}")
