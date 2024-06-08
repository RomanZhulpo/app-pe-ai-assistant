import os
from dotenv import load_dotenv
import logging
import sys
from pathlib import Path

# Add the project root to the system path for module resolution
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

# Import custom modules
from logging_config import setup_logging

# Setup logging configuration
setup_logging()
logger = logging.getLogger(__name__)

class OpenAI_API:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        self.api_key = os.getenv('OPENAI_API_KEY')  # Get API key from environment variables
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',  # Set authorization header
            'Content-Type': 'application/json'  # Set content type to JSON
        }
        logger.info("OpenAI_API initialized successfully.")

    def make_request(self, endpoint, data, method='POST'):
        import requests
        url = f'https://api.openai.com/v1/{endpoint}'  # Construct the full URL
        logger.info(f"Making {method} request to {url}")
        logger.debug(f"Making {method} request to {url} with data: {data}")
        if method == 'POST':
            response = requests.post(url, headers=self.headers, json=data)  # Make a POST request
        elif method == 'GET':
            response = requests.get(url, headers=self.headers, params=data)  # Make a GET request
        logger.info(f"Received response: {response.status_code}")
        logger.debug(f"Received response: {response.status_code} - {response.text}")
        return response.json()  # Return the response as JSON

    def chat_completion(self, messages, model="gpt-4-turbo", temperature=0.7):
        # Generate text completion using OpenAI's GPT model
        data = {
            'model': model,
            'messages': messages,
            'temperature': temperature
        }
        return self.make_request('chat/completions', data)  # Make a request to the chat completions endpoint

    def check_api_status(self):
        # Check the availability of the OpenAI API
        try:
            response = self.make_request('models', {}, 'GET')  # Make a GET request to the models endpoint
            if response.get('error'):
                logger.error(f"OpenAI API check failed: {response['error']}")  # Log an error if the API check fails
                return False
            logger.info("OpenAI API is available.")
            return True
        except Exception as e:
            logger.error(f"OpenAI API check exception: {e}")  # Log an exception if one occurs
            return False