import datetime
import os
import sys


from dotenv import load_dotenv
from openai_api import OpenAI_API
from pathlib import Path
from prompt_templates import public_holiday_prompt_template

project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from src.data.db_functions import DBConnection
from src.utils.google_space_webhook import GoogleChatWebhook  


load_dotenv()  # Загрузка переменных из .env файла
class PublicHoliday:
    def __init__(self, db_connection, webhook_url):
        self.db = db_connection
        self.webhook = GoogleChatWebhook(webhook_url)  # Инициализация webhook

    def find_holidays(self, date=None):
        if date is None:
            date = datetime.datetime.now().strftime('%Y-%m-%d')
        query = f"""
        SELECT h.name AS holiday_name, p.name AS location_name, p.country_code AS location_code, h.occurs_on AS holiday_date
        FROM All_Holidays AS h
        JOIN HolidayPolicies AS p ON h.holiday_policy_id = p.id
        WHERE h.occurs_on = '{date}'
        """
        result = self.db.execute(query)
        holidays = result.fetchall()
        if not holidays:
            return []  # Возвращаем пустой список, если праздников нет
        # Преобразование результатов в список словарей
        holidays_info = [{'holiday_date': row['holiday_date'], 'holiday_name': row['holiday_name'], 'location_name': row['location_name'], 'location_code': row['location_code']} for row in holidays]
        print("Найденные праздники:", holidays_info)  # Вывод результатов в консоль
        return holidays_info

    def generate_holiday_message(self, date=None):
        holidays = self.find_holidays(date)
        if not holidays:
            if date is None:
                date = datetime.datetime.now().strftime('%Y-%m-%d')
            message = f"On {date} there are no public holidays in Paysera locations."
            print(message)  # Вывод сообщения на экран
            return message

        messages = []
        api = OpenAI_API()
        for holiday in holidays:
            # Формирование запроса с использованием шаблона
            prompt = public_holiday_prompt_template.format(
                holiday_date=holiday['holiday_date'],
                holiday_name=holiday['holiday_name'],
                location_name=holiday['location_name'],
                location_code=holiday['location_code']
            )
            prompt_data = [{"role": "user", "content": prompt}]
            response = api.chat_completion(prompt_data)
            # Извлечение текста сообщения из ответа
            message = response.get('choices')[0].get('message') if response.get('choices') else "Error in generating message."
            messages.append(message)
            print(message)  # Вывод сообщения на экран

        return messages

    def generate_and_send_holiday_message(self, date=None):
        raw_messages = self.generate_holiday_message(date)
        if isinstance(raw_messages, str):
            # Если сообщение - строка, значит, это сообщение об отсутствии праздников
            # Отправка сообщения в Google Chat
            response = self.webhook.send_message(raw_messages)
            print("Статус отправки:", response.status_code)  # Вывод статуса отправки
            return response
        else:
            # Обработка списка строк, полученных от API
            responses = []
            for raw_message in raw_messages:
                # Извлечение текста сообщения из объекта "content"
                message = raw_message['content']
                # Отправка каждого сообщения отдельно в Google Chat
                response = self.webhook.send_message(message)
                print("Статус отправки:", response.status_code)  # Вывод статуса отправки
                responses.append(response)
            return responses

# Пример вызова
if __name__ == "__main__":
    from src.data.db_functions import DBConnection
    db = DBConnection()
    webhook_url = os.getenv("WEBHOOK_URL")  # Получение URL из переменной окружения
    public_holiday = PublicHoliday(db, webhook_url)
    specific_date = '2024-05-31'
    responses = public_holiday.generate_and_send_holiday_message(specific_date)
    for response in responses:
        print("Ответ сервера:", response.json())  # Вывод ответа сервера для каждого сообщения
