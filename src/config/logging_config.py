import logging
import os

def setup_logging():
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'app-pe-ai-assistant.log')

    logging.basicConfig(level=logging.DEBUG,
                        handlers=[
                            logging.FileHandler(log_file, mode='w'),
                            logging.StreamHandler()
                        ],
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')