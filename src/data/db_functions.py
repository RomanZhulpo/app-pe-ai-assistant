import sqlite3
import logging
import sys
import os
from pathlib import Path

# Add the project root directory to the sys.path
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from src.config.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global variable for database path
db_path = project_root / os.getenv("DB_PATH")

class DBConnection:
    def __init__(self):
        self.db_path = db_path  # Сохраняем путь к базе данных в экземпляре класса
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row  # Установка row_factory для доступа к данным по именам столбцов
        self.cursor = self.connection.cursor()

    def execute(self, query, params=None):
        # Создание нового соединения для каждого запроса
        with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
            conn.row_factory = sqlite3.Row  # Установка row_factory для нового соединения
            cursor = conn.cursor()
            if params:
                result = cursor.execute(query, params)
            else:
                result = cursor.execute(query)
            conn.commit()
        return result.fetchall()  # Возвращаем результаты запроса

    def check_database(self):
        # Проверка доступности базы данных с созданием нового соединения
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database check failed: {e}")
            return False

# Create database
def create_database():
    try:
         # Ensure the 'db' directory exists
        db_dir = db_path.parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Employees (
                id INTEGER PRIMARY KEY,
                active INTEGER,
                employee_number TEXT,
                full_name TEXT,
                first_name TEXT,
                last_name TEXT,
                email TEXT,
                date_of_birth DATE,
                gender TEXT,
                avatar_url TEXT,
                probation_ends_on DATE,
                hired_on DATE,
                slack_username TEXT,
                linkedin_url TEXT,
                position_name TEXT,
                job_level TEXT,
                division TEXT,
                location_id INTEGER,
                employment_type TEXT,
                department TEXT,
                manager_id INTEGER,
                created_at DATETIME,
                updated_at DATETIME)
            ''')
            # Create Locations table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Locations (
                id INTEGER PRIMARY KEY,
                name TEXT,
                address TEXT,
                time_zone TEXT,
                holiday_policy_id INTEGER,
                created_at DATETIME,
                updated_at DATETIME)
            ''')
            # Create HolidayPolicies tableåß
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS HolidayPolicies (
                id INTEGER PRIMARY KEY,
                name TEXT,
                country_code TEXT,
                created_at DATETIME,
                updated_at DATETIME)
            ''')
            # Create Holidays table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS All_Holidays (
                id INTEGER PRIMARY KEY,
                name TEXT,
                occurs_on DATE,
                starts_on DATE,
                ends_on DATE,
                is_working BOOLEAN,
                compensated_on DATE,
                observed_on DATE,
                holiday_policy_id INTEGER,
                created_at DATETIME,
                updated_at DATETIME)
        ''')

            conn.commit()
        logging.info("Database created successfully.")
    except Exception as e:
        logging.error(f"Error creating database: {e}")
        raise e