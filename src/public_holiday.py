import datetime
import logging
import os
from dotenv import load_dotenv
from pathlib import Path
from db_functions import DBConnection
from google_space_webhook import GoogleChatWebhook
from logging_config import setup_logging
from prompt_templates import public_holiday_prompt_template, public_holiday_prompt_template_v2
from openai_api import OpenAI_API
import json
import re

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
            return []  # Return empty list instead of None

    def determine_holiday_similarity(self, holidays):
        if not holidays:
            logging.info("No holidays to check for similarity.")
            return None
        
        logging.debug(f"Holiday list for similarity check: {holidays}")

        # Преобразуем список праздников в строку
        holidays_str = json.dumps(holidays, indent=2)
        
        # Формируем запрос для OpenAI
        try:
            # Используем простую конкатенацию строк вместо format
            prompt = public_holiday_prompt_template_v2 + "\n\nHoliday list:\n" + holidays_str
            logging.debug(f"Generated prompt for OpenAI: {prompt}")
        except Exception as e:
            logging.error(f"Error creating prompt: {e}", exc_info=True)
            return None

        # Отправляем запрос в OpenAI API
        prompt_data = [{"role": "user", "content": prompt}]
        try:
            response = self.api.chat_completion(prompt_data)
        except Exception as e:
            logging.error(f"Error calling OpenAI API: {e}")
            return None

        logging.debug(f"AI response for holiday similarity: {response}")

        # Проверяем и возвращаем ответ
        if 'choices' in response and response['choices'] and 'message' in response['choices'][0] and 'content' in response['choices'][0]['message']:
            return response['choices'][0]['message']['content']
        else:
            logging.error("AI did not return a valid response for holiday similarity")
            return None

    def _check_api_response(self, response):
        if 'choices' in response and response['choices'] and 'message' in response['choices'][0] and 'content' in response['choices'][0]['message']:
            return response['choices'][0]['message']['content']
        else:
            logging.error("API did not return a valid response or missing 'content'")
            return None

    def generate_holiday_message(self, date=None):
        holidays = self.find_holidays(date)
        if holidays is None:
            message = "Error occurred while finding holidays."
            logging.error(message)
            return message
        if not holidays:
            message = f"On {date} there are no public holidays in Paysera locations."
            logging.info(message)
            return message

        similarity_response = self.determine_holiday_similarity(holidays)
        if similarity_response is None:
            return "Error in determining holiday similarity."

        try:
            # Извлекаем JSON из ответа OpenAI
            json_match = re.search(r'```json\n(.*?)\n```', similarity_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                similarity_data = json.loads(json_str)
            else:
                raise ValueError("No JSON found in the response")

            if 'holidays' not in similarity_data:
                raise KeyError("'holidays' key not found in similarity data")
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logging.error(f"Error processing holiday similarity response: {e}", exc_info=True)
            return "Error in processing holiday similarity response."

        logging.debug(f"Similarity data: {similarity_data}")

        messages = []
        for holiday in similarity_data['holidays']:
            locations = ', '.join(holiday['locations'])
            prompt = public_holiday_prompt_template.format(
                holiday_date=holidays[0]['holiday_date'],
                holiday_name=holiday['holiday_name'],
                location_name=locations,
                location_code=''  # Not needed as we list all locations
            )
            prompt_data = [{"role": "user", "content": prompt}]
            response = self.api.chat_completion(prompt_data)
            logging.debug(f"API response: {response}")

            message = self._check_api_response(response)
            if not isinstance(message, str):
                logging.error("Generated message is not a string")
                continue

            messages.append(message)
            logging.info(f"Announcement for holiday '{holiday['holiday_name']}' generated.")
        return messages

    def generate_and_send_holiday_message(self, date=None):
        raw_messages = self.generate_holiday_message(date)
        if isinstance(raw_messages, str):
            if "Error" in raw_messages:
                logging.error(raw_messages)
                return None  # Do not send message if there was an error
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
    specific_date = '2024-06-17' 
    responses = public_holiday.generate_and_send_holiday_message(specific_date)
    if responses:
        for response in responses:
            logging.debug(f"Server response status: {response.status_code if hasattr(response, 'status_code') else 'No status code available'}")
    else:
        logging.error("Failed to send holiday messages due to an error.")
