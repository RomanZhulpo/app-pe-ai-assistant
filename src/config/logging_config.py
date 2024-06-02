import logging
from dotenv import load_dotenv, dotenv_values
import os
from pathlib import Path

# Set the project root directory
project_root = Path(__file__).resolve().parents[2]
load_dotenv()  # Load environment variables from .env file

logging_initialized = False

def setup_logging():
    global logging_initialized
    if not logging_initialized:
        # Get log level from environment variable, default to 'DEBUG'
        log_level = os.getenv('LOG_LEVEL', 'DEBUG').upper()
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)  # Ensure the log directory exists
        log_file = os.path.join(log_dir, 'app-pe-ai-assistant.log')

        # Configure logging settings
        logging.basicConfig(
            level=getattr(logging, log_level),
            handlers=[
                logging.FileHandler(log_file, mode='w'),  # Log to file
                logging.StreamHandler()  # Log to console
            ],
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logging_initialized = True

def reload_env_and_logging():
    # Load new values from .env file
    env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')  # Path to your .env file
    new_env = dotenv_values(env_path)
    
    # Update environment variables
    os.environ.update(new_env)
    
    # Reinitialize logging
    setup_logging()

# Call the function to reload environment variables and logging configuration
reload_env_and_logging()
