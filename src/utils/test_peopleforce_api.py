import os
import sys
from peopleforce_api import PeopleForceAPI
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Add the project root directory to the sys.path
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from src.utils.peopleforce_api import PeopleForceAPI

def main():
    # Убедитесь, что переменные окружения установлены
    # Отладочный вывод переменных окружения
    print(f"PEOPLEFORCE_API_URL: {os.getenv('PEOPLEFORCE_API_URL')}")
    print(f"PEOPLEFORCE_API_KEY: {os.getenv('PEOPLEFORCE_API_KEY')}")

    # Инициализация API
    api = PeopleForceAPI()

    # Тестирование методов
    try:
        #print("Listing all employees with params:")
        #params = {"ids[]": "224526", "status": "active", "page": "1"}
        #employees = api.list_all_employees(params=params)
        #print(employees)

        print("\nGetting an employee with ID 1:")
        employee = api.get_employee(224526)
        print(employee)

        print("\nListing holidays for employee with ID 1:")
        holidays = api.list_employee_holidays(224526)
        print(holidays)

        print("\nListing all locations:")
        locations = api.list_all_locations()
        print(locations)

        print("\nListing all holidays:")
        holidays = api.list_all_holidays()
        print(holidays)

        print("\nListing company calendar events:")
        events = api.list_company_calendar_events()
        print(events)

        print("\nListing all teams:")
        teams = api.list_all_teams()
        print(teams)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()