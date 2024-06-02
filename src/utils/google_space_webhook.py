import os
import requests
import json
import sys
from pathlib import Path
import logging

# Add the project root to the system path for module resolution
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

# Import custom logging configuration
from src.config.logging_config import setup_logging  # Ensure the import path is correct

# Setup logging configuration
setup_logging()
logger = logging.getLogger(__name__)  # Create a logger for this module

class GoogleChatWebhook:
    def __init__(self, webhook_url):
        self.url = webhook_url

    def send_message(self, message):
        # Ensure the message is a string
        if not isinstance(message, str):
            logger.error("The message to be sent must be a string")
            return None

        app_message = {"text": message}
        try:
            # Send the message to the webhook URL
            response = requests.post(self.url, json=app_message)
            logger.debug(f"Message being sent: {json.dumps(app_message)}")
            logger.debug(f"Server response: {response.status_code}, {response.text}")
            
            if response.status_code != 200:
                logger.error(f"Error sending message: {response.text}")
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Error while sending message: {e}")
            return None

if __name__ == "__main__":
    # Get the webhook URL from environment variables
    webhook_url = os.getenv("WEBHOOK_URL")
    webhook = GoogleChatWebhook(webhook_url)
    response = webhook.send_message("Hello from Python script!")
    if response:
        logger.info(f"Response status: {response.status_code}")
