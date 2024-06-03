import logging
from flask import Flask
from flask_apscheduler import APScheduler
import os
from pathlib import Path
import sys

# Add the project root to the system path for module resolution
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

# Import custom modules
from src.genai.happy_birthday import HappyBirthday
from src.data.db_functions import DBConnection
from src.config.logging_config import setup_logging
from src.utils.healthcheck import healthcheck  
from src.genai.public_holiday import PublicHoliday 

# Setup logging configuration
setup_logging()
logger = logging.getLogger(__name__)

logger.info("Starting Flask application setup")

# Initialize Flask application
app = Flask(__name__)

# Initialize and start the APScheduler
scheduler = APScheduler()

def initialize_scheduler():
    if not scheduler.running:
        scheduler.init_app(app)
        scheduler.start()
        logger.debug("Scheduler initialized and started")

# Initialize database connection
db_connection = DBConnection()

# Get webhook URL from environment variables
webhook_url = os.getenv("WEBHOOK_URL")

# Initialize birthday and public holiday handlers
birthday_celebrator = HappyBirthday(db_connection, webhook_url)
public_holiday = PublicHoliday(db_connection, webhook_url)

# Function to schedule birthday wishes
def schedule_birthday_wishes():
    logger.info("Scheduling birthday wishes")
    birthday_celebrator.send_birthday_wishes()

# Function to schedule public holiday messages
def schedule_public_holidays():
    logger.info("Scheduling public holiday messages")
    public_holiday.generate_and_send_holiday_message()

# Function to get scheduling times from environment variables
def get_schedule_time(env_var, default):
    value = int(os.getenv(env_var, default))
    logger.info(f"{env_var} is set to {value}")
    return value

def schedule_jobs():
    # Schedule the birthday wishes job
    if not scheduler.get_job('birthday_wish_job'):
        scheduler.add_job(
            func=schedule_birthday_wishes, 
            trigger='cron', 
            hour=get_schedule_time("BIRTHDAY_HOUR", 21), 
            minute=get_schedule_time("BIRTHDAY_MINUTE", 49), 
            timezone='UTC',
            id='birthday_wish_job'
        )
        logger.info("Birthday wishes job scheduled")

    # Schedule the public holiday messages job
    if not scheduler.get_job('public_holiday_message_job'):
        scheduler.add_job(
            func=schedule_public_holidays, 
            trigger='cron', 
            hour=get_schedule_time("HOLIDAY_HOUR", 21), 
            minute=get_schedule_time("HOLIDAY_MINUTE", 49), 
            timezone='UTC',
            id='public_holiday_message_job'  
        )
        logger.info("Public holiday messages job scheduled")

# Register healthcheck blueprint
app.register_blueprint(healthcheck)

if __name__ == "__main__":
    initialize_scheduler()
    schedule_jobs()
    logger.info("Running the Flask application")
    app.run(host='0.0.0.0', port=8080, debug=False)
