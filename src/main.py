import logging
from flask import Flask
from flask_apscheduler import APScheduler
import os
from pathlib import Path
import sys
from dotenv import load_dotenv

# Add the project root to the system path for module resolution
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

# Load environment variables from .env file
load_dotenv(dotenv_path=project_root / '.env')

# Import custom modules
from happy_birthday import HappyBirthday
from db_functions import DBConnection, create_database
from logging_config import setup_logging
from healthcheck import healthcheck  
from public_holiday import PublicHoliday 
from import_data import PeopleForceDataImporter

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

# Function to ensure database and tables are created
def ensure_database_setup():
    if not db_connection.check_database():
        logger.info("Database not found or not accessible. Creating database and importing data.")
        create_database()
        PeopleForceDataImporter().update_data_from_api()
    else:
        logger.info("Database is available and accessible.")
        # Check if the required tables exist
        required_tables = ["All_Holidays", "Employees", "HolidayPolicies", "Locations"]
        for table in required_tables:
            if not db_connection.check_table_exists(table):
                logger.info(f"Table {table} not found. Creating database and importing data.")
                create_database()
                PeopleForceDataImporter().update_data_from_api()
                break

# Function to schedule daily data update
def schedule_daily_data_update():
    if not scheduler.get_job('daily_data_update'):
        scheduler.add_job(
            func=PeopleForceDataImporter().update_data_from_api,
            trigger='cron',
            hour=get_schedule_time("DAILY_UPDATE_HOUR", 6),  # Get the hour from environment variables
            minute=get_schedule_time("DAILY_UPDATE_MINUTE", 0),  # Get the minute from environment variables
            timezone='UTC',
            id='daily_data_update'
        )
        logger.info("Daily data update job scheduled")

# Get webhook URL from environment variables
webhook_url = os.getenv("WEBHOOK_URL")

# Get notify_if_none parameter from environment variables
notify_if_none = os.getenv("NOTIFY_IF_NONE", "false").lower() == "true"  # Convert to boolean

# Initialize birthday and public holiday handlers
birthday_celebrator = HappyBirthday(db_connection, webhook_url)
public_holiday = PublicHoliday(db_connection, webhook_url)

# Function to schedule birthday wishes
def schedule_birthday_wishes():
    logger.info("Scheduling birthday wishes")
    try:
        birthday_celebrator.send_birthday_wishes(notify_if_none=notify_if_none)  # Pass the notify_if_none parameter
    except Exception as e:
        logger.error(f"Error scheduling birthday wishes: {e}", exc_info=True)

# Function to schedule public holiday messages
def schedule_public_holidays():
    logger.info("Scheduling public holiday messages")
    try:
        public_holiday.generate_and_send_holiday_message()
    except Exception as e:
        logger.error(f"Error scheduling public holiday messages: {e}", exc_info=True)

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
            hour=get_schedule_time("BIRTHDAY_HOUR", 7), 
            minute=get_schedule_time("BIRTHDAY_MINUTE", 0), 
            timezone='UTC',
            id='birthday_wish_job'
        )
        logger.info("Birthday wishes job scheduled")

    # Schedule the public holiday messages job
    if not scheduler.get_job('public_holiday_message_job'):
        scheduler.add_job(
            func=schedule_public_holidays, 
            trigger='cron', 
            hour=get_schedule_time("HOLIDAY_HOUR", 7), 
            minute=get_schedule_time("HOLIDAY_MINUTE", 1), 
            timezone='UTC',
            id='public_holiday_message_job'  
        )
        logger.info("Public holiday messages job scheduled")

# Register healthcheck blueprint
app.register_blueprint(healthcheck)

if __name__ == "__main__":
    try:
        ensure_database_setup()
        initialize_scheduler()
        schedule_daily_data_update()
        schedule_jobs()
        logger.info("Running the Flask application")
        app.run(host='0.0.0.0', port=8080, debug=False)
    except Exception as e:
        logger.error(f"Failed to start the Flask application: {e}", exc_info=True)
