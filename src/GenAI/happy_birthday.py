import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from pathlib import Path


project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from src.data.db_functions import DBConnection
from src.utils.google_space_webhook import GoogleChatWebhook  
from src.config.logging_config import setup_logging
from src.genai.openai_api import OpenAI_API
from src.genai.prompt_templates import HB_prompt_template
import argparse  # Import for command-line argument parsing

setup_logging()
load_dotenv()  # Load environment variables from .env file

logging.info("Logging is set up.")
class HappyBirthday:
    def __init__(self, db_connection, webhook_url):
        self.db = db_connection
        self.webhook = GoogleChatWebhook(webhook_url)  # Initialize webhook

    def find_birthdays(self, date=None):
        if date is None:
            date = datetime.now().strftime('%m-%d')  # Default to today's date in '%m-%d' format
        else:
            try:
                # Ensure the date is in the correct format and reformat it
                date = datetime.strptime(date, '%Y-%m-%d').strftime('%m-%d')
            except ValueError:
                logging.error("Incorrect date format, should be YYYY-MM-DD")
                return []

        logging.info(f"Checking for birthdays on: {date}")  # Log the date being checked
        query = '''
            SELECT id, full_name, date_of_birth, gender, position_name, department, hired_on FROM Employees
            WHERE strftime('%m-%d', date_of_birth) = ? AND active = 1 AND division = "Paysera Engineering"
        '''
        result = self.db.execute(query, (date,))
        return result
    
    @staticmethod
    def calculate_anniversaries(hired_on, current_date=None):
        if current_date is None:
            current_date = datetime.now()
        else:
            current_date = datetime.strptime(current_date, '%Y-%m-%d')

        hired_on = datetime.strptime(hired_on, '%Y-%m-%d')
        years_difference = current_date.year - hired_on.year

        if (hired_on.month, hired_on.day) > (current_date.month, current_date.day):
            years_difference -= 1

        return years_difference + 1

    def generate_birthday_wishes(self, employee, current_date=None):
        # Calculate the number of anniversaries
        anniversaries = HappyBirthday.calculate_anniversaries(employee['hired_on'], current_date)

        # Anonymize employee data and add the number of anniversaries
        employee_data_anonymized = (
            f"Department: {employee['department']}, "
            f"Position: {employee['position_name']}, "
            f"Gender: {employee['gender']}, "
            f"Date of Birthday: {employee['date_of_birth']}, "
            f"Hired On: {employee['hired_on']}, "
            f"Anniversaries: {anniversaries}"
        )

        # Formulate the prompt using the template and anonymized data
        prompt = HB_prompt_template.format(employee_data=employee_data_anonymized)

        # Log the generated prompt
        logging.debug(f"Generated prompt for OpenAI: {prompt}")

        # Create OpenAI client and send the request
        openai_client = OpenAI_API()
        response = openai_client.chat_completion(messages=[{"role": "user", "content": prompt}])

        # Log the received response
        generated_response = response['choices'][0]['message']['content']
        logging.debug(f"Response from OpenAI: {generated_response}")

        # Formulate personalized birthday wishes
        personalized_wishes = f"*{employee['full_name']}*, {generated_response}"
        return personalized_wishes

    def send_birthday_wishes(self, date=None):
        today_birthdays = self.find_birthdays(date)
        if not today_birthdays:
            message = "There are *NO* birthdays at Paysera Engineering today."
            self.webhook.send_message(message)
            logging.info(message)  # Log the absence of birthdays
        else:
            for employee in today_birthdays:
                logging.info(f"Today is the birthday of {employee['full_name']} in {employee['department']}.")  # Log employee's birthday
                birthday_wish = self.generate_birthday_wishes(employee)
                message = f"{birthday_wish}"
                self.webhook.send_message(message)
                logging.info(f"Birthday message sent to Google Chat for {employee['full_name']}.")  # Log the message sending

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send birthday wishes to employees.')
    parser.add_argument('--date', type=str, help='Date to check birthdays for, format YYYY-MM-DD', default=None)
    args = parser.parse_args()

    logging.info(f"Script started with date: {args.date}")  # Log the provided date

    db = DBConnection()
    webhook_url = os.getenv("WEBHOOK_URL")  # Get the webhook URL from environment variables
    birthday_celebrator = HappyBirthday(db, webhook_url)
    birthday_celebrator.send_birthday_wishes(args.date)
