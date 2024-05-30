import os
from dotenv import load_dotenv
import requests

load_dotenv()  # Загрузка переменных из .env файла

class GoogleChatWebhook:
    def __init__(self, webhook_url):
        # Инициализация с полным URL для webhook
        self.url = webhook_url

    def send_message(self, message):
        # Логирование отправляемого сообщения для отладки
       #print("Отправляемое сообщение:", json.dumps({"text": message}))

        # Отправка сообщения в Google Chat
        app_message = {"text": message}
        response = requests.post(self.url, json=app_message)
        #print("Ответ сервера:", response.status_code, response.text)  # Логирование ответа сервера
        return response

# Пример использования
if __name__ == "__main__":
    webhook_url = os.getenv("WEBHOOK_URL")
    webhook = GoogleChatWebhook(webhook_url)
    response = webhook.send_message("Привет от Python скрипта!")
    #print(response.text)  # Вывод ответа от сервера

