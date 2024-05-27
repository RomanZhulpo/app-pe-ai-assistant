import datetime
from openai_api import OpenAI_API
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from src.data.db_functions import DBConnection

class PublicHoliday:
    def __init__(self, db_connection):
        self.db = db_connection

    def find_holidays(self, date=None):
        if date is None:
            date = datetime.datetime.now().strftime('%Y-%m-%d')
        query = f"SELECT * FROM All_Holidays WHERE occurs_on = '{date}'"
        result = self.db.execute(query)
        return result.fetchall()

    def generate_holiday_message(self, date=None):
        holidays = self.find_holidays(date)
        if not holidays:
            if date is None:
                date = datetime.datetime.now().strftime('%Y-%m-%d')
            return f"На {date} нет публичных выходных в локациях Paysera."
        
        messages = []
        api = OpenAI_API()
        for holiday in holidays:
            prompt = f"Сегодня {holiday['occurs_on']} - {holiday['name']} в {holiday['location']}. Краткая историческая справка:"
            completion = api.chat_completion(prompt)
            messages.append(completion)
        
        return " ".join(messages)

# Пример вызова
if __name__ == "__main__":
    from src.data.db_functions import DBConnection
    db = DBConnection()
    public_holiday = PublicHoliday(db)
    specific_date = '2024-05-28'
    message = public_holiday.generate_holiday_message(specific_date)
    print(message)