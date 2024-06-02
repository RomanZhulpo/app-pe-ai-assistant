import datetime
import os
import sys
from dotenv import load_dotenv
import logging
from pathlib import Path

# Set up project root path
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

# Import custom modules
from src.data.db_functions import DBConnection
from src.utils.google_space_webhook import GoogleChatWebhook
from src.config.logging_config import setup_logging
from src.genai.prompt_templates import public_holiday_prompt_template
from src.genai.openai_api import OpenAI_API

# Load environment variables and setup logging
load_dotenv()
setup_logging()

class PublicHoliday:
    def __init__(self, db_connection, webhook_url):
        self.db = db_connection
        self.webhook = GoogleChatWebhook(webhook_url)  # Initialize webhook
        self.api = OpenAI_API()  # Initialize OpenAI API
        logging.info("PublicHoliday initialized with given database connection, webhook URL, and OpenAI API.")

    def find_holidays(self, date=None):
        if date is None:
            date = datetime.datetime.now().strftime('%Y-%m-%d')  # Default to today's date
        logging.info(f"Searching for public holidays on: {date}")
        query = """
        SELECT h.name AS holiday_name, p.name AS location_name, p.country_code AS location_code, h.occurs_on AS holiday_date
        FROM All_Holidays AS h
        JOIN HolidayPolicies AS p ON h.holiday_policy_id = p.id
        WHERE h.occurs_on = ?
        """
        try:
            result = self.db.execute(query, (date,))
            holidays = result
            if not holidays:
                logging.info("No public holidays found.")
                return []
            holidays_info = [{'holiday_date': row['holiday_date'], 'holiday_name': row['holiday_name'], 'location_name': row['location_name'], 'location_code': row['location_code']} for row in holidays]
            logging.info(f"Found holidays: {holidays_info}")
            return holidays_info
        except Exception as e:
            logging.error("Error finding holidays", exc_info=True)
            return []

    def generate_holiday_message(self, date=None):
        holidays = self.find_holidays(date)
        if not holidays:
            message = f"On {date} there are no public holidays in Paysera locations."
            logging.info(message)
            return message

        messages = []
        for holiday in holidays:
            # Format the prompt using the template and holiday data
            prompt = public_holiday_prompt_template.format(
                holiday_date=holiday['holiday_date'],
                holiday_name=holiday['holiday_name'],
                location_name=holiday['location_name'],
                location_code=holiday['location_code']
            )
            prompt_data = [{"role": "user", "content": prompt}]
            response = self.api.chat_completion(prompt_data)
            logging.debug(f"API response: {response}")  # Log the full API response

            if 'choices' in response and response['choices'] and 'message' in response['choices'][0] and 'content' in response['choices'][0]['message']:
                message_content = response['choices'][0]['message']['content']
                message = message_content
            else:
                message = "Error in generating message."
                logging.error("API did not return a valid response or missing 'content'")

            logging.debug(f"Generated message for {holiday['holiday_name']} on {holiday['holiday_date']}: {message}")

            if not isinstance(message, str):
                logging.error("Generated message is not a string")
                continue

            messages.append(message)
            logging.info(f"Announcement for holiday '{holiday['holiday_name']}' generated.")
        return messages

    def generate_and_send_holiday_message(self, date=None):
        raw_messages = self.generate_holiday_message(date)
        if isinstance(raw_messages, str):
            logging.debug(f"Generated message: {raw_messages}")
            response = self.webhook.send_message(raw_messages)
            logging.info(f"Message sent status: {response.status_code if hasattr(response, 'status_code') else 'No status code available'}")
            return response
        else:
            responses = []
            for raw_message in raw_messages:
                response = self.webhook.send_message(raw_message)
                logging.info(f"Message sent status: {response.status_code if hasattr(response, 'status_code') else 'No status code available'}")
                responses.append(response)
            return responses

if __name__ == "__main__":
    db = DBConnection()
    webhook_url = os.getenv("WEBHOOK_URL")  # Get the webhook URL from environment variables
    public_holiday = PublicHoliday(db, webhook_url)
    specific_date = '2024-06-03'
    responses = public_holiday.generate_and_send_holiday_message(specific_date)
    for response in responses:
        if hasattr(response, 'json'):
            logging.debug(f"Server response: {response.json()}")
        else:
            logging.error("Response object does not have a .json() method")
