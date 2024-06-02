from flask import Blueprint
from pathlib import Path
import sys
import logging

# Add the project root to the system path for module resolution
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

# Import custom modules
from src.config.logging_config import setup_logging
from src.data.db_functions import DBConnection
from src.genai.openai_api import OpenAI_API
from src.utils.peopleforce_api import PeopleForceAPI

# Initialize logging configuration
setup_logging()
logger = logging.getLogger(__name__)

# Create a Flask Blueprint for health checks
healthcheck = Blueprint('healthcheck', __name__)

@healthcheck.route('/health')
def health_check():
    """Endpoint to check if the service is up"""
    logger.info("Health check requested")
    return 'OK', 200

@healthcheck.route('/ready')
def readiness_check():
    """Endpoint to check if all dependencies are ready"""
    # Check database availability
    db = DBConnection()
    if not db.check_database():
        logger.error("Database is not ready")
        return 'DB down', 500

    # Check OpenAI API availability
    openai_api = OpenAI_API()
    if not openai_api.check_api_status():
        logger.error("OpenAI API is not ready")
        return 'OpenAI API down', 500

    # Check PeopleForce API availability
    peopleforce_api = PeopleForceAPI()
    if not peopleforce_api.check_api_status():
        logger.error("PeopleForce API is not ready")
        return 'PeopleForce API down', 500

    logger.info("All systems ready")
    return 'OK', 200

@healthcheck.route('/ping')
def ping_pong():
    """Endpoint to check basic connectivity"""
    logger.info("Ping request received")
    return 'Pong', 200

if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(healthcheck)
    app.run(debug=True)