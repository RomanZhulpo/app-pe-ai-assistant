import logging
from flask import Flask
from flask_apscheduler import APScheduler
import os
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from src.genai.happy_birthday import HappyBirthday
from src.data.db_functions import DBConnection
from src.config.logging_config import setup_logging
from src.utils.healthcheck import healthcheck  # Убедитесь, что путь импорта корректен
from src.genai.public_holiday import PublicHoliday  # Убедитесь, что импортирован правильно

# Настройка логгирования
setup_logging()
logger = logging.getLogger(__name__)

logger.info("Starting Flask application setup")

app = Flask(__name__)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

logger.debug("Scheduler initialized and started")

db_connection = DBConnection()
webhook_url = os.getenv("WEBHOOK_URL")
birthday_celebrator = HappyBirthday(db_connection, webhook_url)
public_holiday = PublicHoliday(db_connection, webhook_url)  # Предполагается, что db_connection и webhook_url уже инициализированы

def schedule_birthday_wishes():
    logger.info("Scheduling birthday wishes")
    birthday_celebrator.send_birthday_wishes()

def schedule_public_holidays():
    logger.info("Scheduling public holiday messages")
    public_holiday.generate_and_send_holiday_message()

scheduler.add_job(
    func=schedule_birthday_wishes, 
    trigger='cron', 
    hour=21, 
    minute=49, 
    timezone='UTC',
    id='birthday_wish_job'  # Уникальный идентификатор задачи
)
logger.info("Birthday wishes job scheduled")

# Добавление задачи в APScheduler
scheduler.add_job(
    func=schedule_public_holidays, 
    trigger='cron', 
    hour=21, 
    minute=49, 
    timezone='UTC',
    id='public_holiday_message_job'  # Уникальный идентификатор задачи
)
logger.info("Public holiday messages job scheduled")

# Регистрация Blueprint
app.register_blueprint(healthcheck)

if __name__ == "__main__":
    logger.info("Running the Flask application")
    app.run(host='0.0.0.0', port=8080, debug=True)