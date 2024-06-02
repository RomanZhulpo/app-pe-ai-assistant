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

# Schedule the birthday wishes job
scheduler.add_job(
    func=schedule_birthday_wishes, 
    trigger='cron', 
    hour=21, 
    minute=49, 
    timezone='UTC',
    id='birthday_wish_job'
)
logger.info("Birthday wishes job scheduled")

# Schedule the public holiday messages job
scheduler.add_job(
    func=schedule_public_holidays, 
    trigger='cron', 
    hour=21, 
    minute=49, 
    timezone='UTC',
    id='public_holiday_message_job'  
)
logger.info("Public holiday messages job scheduled")

# Register healthcheck blueprint
app.register_blueprint(healthcheck)

if __name__ == "__main__":
    logger.info("Running the Flask application")
    app.run(host='0.0.0.0', port=8080, debug=True)