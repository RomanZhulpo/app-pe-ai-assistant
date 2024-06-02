import sqlite3
import logging
from datetime import datetime
from pathlib import Path
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root directory to the sys.path
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

# Import custom modules
from src.config.logging_config import setup_logging
from src.utils.peopleforce_api import PeopleForceAPI
from src.data.db_functions import create_database

# Setup logging configuration
setup_logging()
logger = logging.getLogger(__name__)

# Parse date string to date object
def parse_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else None

# Initialize set to store imported employee IDs
imported_employee_ids = set()
db_path = project_root / os.getenv("DB_PATH")

# Get employees from Peopleforce API and import to database
def import_employees():
    create_database()  # Ensure the database is created
    api = PeopleForceAPI()
    page = 1
    total_imported = 0

    while True:
        params = {
            "status": "active",
            "page": page
        }
        employees_data = api.list_all_employees(params=params).get('data', [])
        if not employees_data:
            break  # If there is no more data, exit the loop

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            for employee in employees_data:
                insert_employee_data(cursor, employee)
            conn.commit()
        total_imported += len(employees_data)
        page += 1  # Go to the next page

    deactivate_missing_employees()  # Deactivate employees not in the imported list
    logging.info(f"Total employees imported: {total_imported}")

# Insert employee data into the database
def insert_employee_data(cursor, employee):
    # Extract dates and convert them to the correct format
    hired_on = parse_date(employee['hired_on'])
    probation_ends_on = parse_date(employee['probation_ends_on'])
    created_at = datetime.strptime(employee['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
    updated_at = datetime.strptime(employee['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ')

    # Extract division and department names from nested objects
    division_name = employee['division']['name'] if employee.get('division') else None
    department_name = employee['department']['name'] if employee.get('department') else None
    position_name = employee['position']['name'] if employee.get('position') else None
    job_level = employee['job_level']['name'] if employee.get('job_level') else None
    manager_id = employee['reporting_to']['id'] if employee.get('reporting_to') else None

    # Extract location information
    location = employee.get('location')
    location_id = None
    if location:
        cursor.execute('''INSERT OR IGNORE INTO Locations (id, name, address, time_zone, holiday_policy_id, created_at, updated_at)
                          VALUES (?, ?, ?, ?, ?, ?, ?)''',
                       (location['id'], location['name'], location['address'], location['time_zone'],
                        location['holiday_policy_id'], 
                        datetime.strptime(location['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'),
                        datetime.strptime(location['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ')))
        location_id = location['id']

    # Insert employee data into the database
    cursor.execute('''INSERT or REPLACE INTO Employees
                          (id, active, employee_number, full_name, first_name, last_name, email, date_of_birth, gender,
                             avatar_url, probation_ends_on, hired_on, slack_username, linkedin_url, position_name, 
                             job_level, division, department, location_id, manager_id, created_at, updated_at)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (employee['id'], employee['active'], employee['employee_number'], employee['full_name'],
                    employee['first_name'], employee['last_name'], employee['email'], employee['date_of_birth'],
                    employee['gender'], employee['avatar_url'], probation_ends_on, hired_on,
                    employee['slack_username'], employee['linkedin_url'], position_name, job_level,
                    division_name, department_name, location_id, manager_id, created_at, updated_at))
    imported_employee_ids.add(employee['id'])

# Function to deactivate missing employees
def deactivate_missing_employees():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        # Create a string with placeholders for the imported employee IDs
        placeholders = ', '.join('?' for _ in imported_employee_ids)
        # Deactivate employees that are not in the imported list
        cursor.execute(f'''
            UPDATE Employees
            SET active = 0
            WHERE id NOT IN ({placeholders})
        ''', tuple(imported_employee_ids))
        conn.commit()

# Import holiday policies from Peopleforce API
def import_holiday_policies_from_api():
    api = PeopleForceAPI()
    holiday_policies = api.list_all_holiday_policies()
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        for policy in holiday_policies['data']:
            cursor.execute('''
                INSERT OR REPLACE INTO HolidayPolicies
                (id, name, country_code, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                policy['id'],
                policy['name'],
                policy['country_code'],
                datetime.strptime(policy['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'),
                datetime.strptime(policy['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
            ))
        conn.commit()

# Import all holidays from Peopleforce API
def import_all_holidays_from_api():
    api = PeopleForceAPI()
    page = 1
    total_imported = 0

    while True:
        all_holidays = api.list_all_holidays(page=page)
        if not all_holidays['data']:
            break  # If there is no more data, exit the loop

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            for holiday in all_holidays['data']:
                cursor.execute('''
                    INSERT OR REPLACE INTO All_Holidays
                    (id, name, occurs_on, starts_on, ends_on, is_working, compensated_on, observed_on, holiday_policy_id, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    holiday['id'],
                    holiday['name'],
                    holiday['occurs_on'],
                    holiday['starts_on'],
                    holiday['ends_on'],
                    not holiday['working'],  # Convert working to is_working, where True means a working day
                    holiday['compensated_on'],
                    holiday['observed_on'],
                    holiday['holiday_policy_id'],
                    datetime.strptime(holiday['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'),
                    datetime.strptime(holiday['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
                ))
            conn.commit()
        total_imported += len(all_holidays['data'])
        page += 1  # Go to the next page
    print(f"Total holidays imported: {total_imported}")


if __name__ == '__main__':
    import_employees()
    import_holiday_policies_from_api()
    import_all_holidays_from_api()