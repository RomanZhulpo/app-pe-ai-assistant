import datetime
import os
import sys
import logging
from dotenv import load_dotenv
from openai_api import OpenAI_API
from pathlib import Path

# Set up project root path
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))
from src.data.db_functions import DBConnection
from src.utils.google_space_webhook import GoogleChatWebhook
from src.config.logging_config import setup_logging
from src.GenAI.prompt_templates import public_holiday_prompt_template

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()



class PublicHoliday:
    def __init__(self, db_connection, webhook_url):
        self.db = db_connection
        self.webhook = GoogleChatWebhook(webhook_url)
        self.api = OpenAI_API()  # Инициализация API здесь
        logging.info("PublicHoliday initialized with given database connection, webhook URL, and OpenAI API.")

    def find_holidays(self, date=None):
        """
        Find public holidays for a given date. If no date is provided, use today's date.
        """
        try:
            if date is None:
                date = datetime.datetime.now().strftime('%Y-%m-%d')
            logging.info(f"Searching for public holidays on: {date}")
            query = """
            SELECT h.name AS holiday_name, p.name AS location_name, p.country_code AS location_code, h.occurs_on AS holiday_date
            FROM All_Holidays AS h
            JOIN HolidayPolicies AS p ON h.holiday_policy_id = p.id
            WHERE h.occurs_on = ?
            """
            result = self.db.execute(query, (date,))
            holidays = result.fetchall()
            if not holidays:
                logging.info("No public holidays found.")
                return []
            holidays_info = [{'holiday_date': row['holiday_date'], 'holiday_name': row['holiday_name'], 'location_name': row['location_name'], 'location_code': row['location_code']} for row in holidays]
            logging.info(f"Found holidays: {holidays_info}")
            return holidays_info
        except Exception as e:
            logging.error(f"Error finding holidays: {e}")
            return []

    def generate_holiday_message(self, date=None):
        """
        Generate messages for public holidays found on a given date.
        """
        holidays = self.find_holidays(date)
        if not holidays:
            message = f"On {date} there are no public holidays in Paysera locations."
            logging.info(message)
            return message

        messages = []
        for holiday in holidays:
            prompt = public_holiday_prompt_template.format(
                holiday_date=holiday['holiday_date'],
                holiday_name=holiday['holiday_name'],
                location_name=holiday['location_name'],
                location_code=holiday['location_code']
            )
            prompt_data = [{"role": "user", "content": prompt}]
            response = self.api.chat_completion(prompt_data)  # Использование существующего экземпляра API
            message = response.get('choices')[0].get('message') if response.get('choices') else "Error in generating message."
            messages.append(message)
            logging.debug(f"Generated message: {message}")
            logging.info(f"Announcement for holiday '{holiday['holiday_name']}' generated.")
        return messages

    def generate_and_send_holiday_message(self, date=None):
        """
        Generate and send holiday messages for a given date.
        """
        raw_messages = self.generate_holiday_message(date)
        if isinstance(raw_messages, str):
            response = self.webhook.send_message(raw_messages)
            logging.info(f"Message sent status: {response.status_code}")
            logging.info("Announcement for holiday sent to Google Chat.")
            return response
        else:
            responses = []
            for raw_message in raw_messages:
                message = raw_message['content']
                response = self.webhook.send_message(message)
                logging.info(f"Message sent status: {response.status_code}")
                logging.info("Announcement sent to Google Chat.")
                responses.append(response)
            return responses

if __name__ == "__main__":
    from src.data.db_functions import DBConnection
    db = DBConnection()
    webhook_url = os.getenv("WEBHOOK_URL") 
    public_holiday = PublicHoliday(db, webhook_url)
    specific_date = '2024-05-30'
    responses = public_holiday.generate_and_send_holiday_message(specific_date)
    for response in responses:
        if hasattr(response, 'json'):
            logging.debug(f"Server response: {response.json()}")
        else:
            logging.error("Response object does not have a .json() method")
