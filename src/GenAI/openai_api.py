import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


class OpenAI_API:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def make_request(self, endpoint, data, method='POST'):
        import requests
        url = f'https://api.openai.com/v1/{endpoint}'
        if method == 'POST':
            response = requests.post(url, headers=self.headers, json=data)
        elif method == 'GET':
            response = requests.get(url, headers=self.headers, params=data)
        return response.json()

    def chat_completion(self, messages, model="gpt-4-turbo", temperature=0.7):
        # Generate text completion using OpenAI's GPT model
        data = {
            'model': model,
            'messages': messages,
            'temperature': temperature
        }
        return self.make_request('chat/completions', data)

    def check_api_status(self):
        # Проверка доступности OpenAI API
        try:
            response = self.make_request('models', {}, 'GET')  # Изменено на GET
            if response.get('error'):
                logger.error(f"OpenAI API check failed: {response['error']}")
                return False
            return True
        except Exception as e:
            logger.error(f"OpenAI API check exception: {e}")
            return False