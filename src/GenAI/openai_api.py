import os
from dotenv import load_dotenv


class OpenAI_API:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def make_request(self, endpoint, data):
        # Make HTTP request to the OpenAI API
        import requests
        response = requests.post(f'https://api.openai.com/v1/{endpoint}', headers=self.headers, json=data)
        return response.json()

    def chat_completion(self, messages, model="gpt-4-turbo", temperature=0.7):
        # Generate text completion using OpenAI's GPT model
        data = {
            'model': model,
            'messages': messages,
            'temperature': temperature
        }
        return self.make_request('chat/completions', data)
