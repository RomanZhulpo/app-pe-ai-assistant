import os
import sys
import requests
import logging
from dotenv import load_dotenv
from pathlib import Path

# Add the project root directory to the sys.path
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

# Import custom logging configuration
from logging_config import setup_logging

# Setup logging configuration
setup_logging()
logger = logging.getLogger(__name__)

# Load environment variables from a .env file
load_dotenv()

class PeopleForceAPI:
    BASE_URL = os.getenv("PEOPLEFORCE_API_URL")  # Base URL for the PeopleForce API
    
    def __init__(self):
        api_key = os.getenv("PEOPLEFORCE_API_KEY")  # API key for authentication
        
        # Debugging environment variables
        logger.debug(f"PEOPLEFORCE_API_URL: {self.BASE_URL}")
        logger.debug(f"PEOPLEFORCE_API_KEY: {api_key}")

        # Check if API key is set
        if not api_key:
            logger.error("API key not found. Please set the PEOPLEFORCE_API_KEY environment variable.")
            raise ValueError("API key not found. Please set the PEOPLEFORCE_API_KEY environment variable.")
        
        # Check if API URL is set
        if not self.BASE_URL:
            logger.error("API URL not found. Please set the PEOPLEFORCE_API_URL environment variable.")
            raise ValueError("API URL not found. Please set the PEOPLEFORCE_API_URL environment variable.")
        
        # Set headers for API requests
        self.headers = {
            "X-API-KEY": api_key,
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        logger.info("PeopleForceAPI initialized successfully.")

    # List all employees
    def list_all_employees(self, params=None):
        url = f"{self.BASE_URL}/employees"
        logger.info(f"Requesting all employees from {url} with params: {params}")
        response = requests.get(url, headers=self.headers, params=params)
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.content}")
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()

    # Get an employee
    def get_employee(self, employee_id):
        url = f"{self.BASE_URL}/employees/{employee_id}"
        logger.info(f"Requesting employee {employee_id} from {url}")
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()

    # List of employee holidays
    def list_employee_holidays(self, employee_id):
        url = f"{self.BASE_URL}/employees/{employee_id}/holidays"
        logger.info(f"Requesting holidays for employee {employee_id} from {url}")
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()

    # List all locations
    def list_all_locations(self):
        url = f"{self.BASE_URL}/locations"
        logger.info(f"Requesting all locations from {url}")
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()

    # List all holidays
    def list_all_holidays(self, page=1):
        url = f"{self.BASE_URL}/holidays?page={page}"
        logger.info(f"Requesting all holidays from {url}")
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()

    # List company calendar events
    def list_company_calendar_events(self):
        url = f"{self.BASE_URL}/calendars"
        logger.info(f"Requesting company calendar events from {url}")
        response = requests.get(url, headers=self.headers)
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.content}")
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()

    # List all holiday policies
    def list_all_holiday_policies(self):
        url = f"{self.BASE_URL}/holiday_policies"
        logger.info(f"Requesting all holiday policies from {url}")
        response = requests.get(url, headers=self.headers)
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.content}")
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()

    # List all teams
    def list_all_teams(self):
        url = f"{self.BASE_URL}/teams"
        logger.info(f"Requesting all teams from {url}")
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()

    def check_api_status(self):
        # Check the availability of the PeopleForce API
        try:
            response = self.list_all_locations()  # Use an existing method to check availability
            if response.get('error'):
                logger.error(f"PeopleForce API check failed: {response['error']}")
                return False
            return True
        except Exception as e:
            logger.error(f"PeopleForce API check exception: {e}")
            return False

if __name__ == "__main__":
    # Initialize the API
    api = PeopleForceAPI()
    print("\nListing all locations:")
    locations = api.list_all_locations()
    print(locations)