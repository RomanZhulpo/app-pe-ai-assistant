# Happy Birthday and Public Holiday Notifier

## Overview

This application is designed to send birthday wishes and public holiday notifications to employees via Google Chat. It uses OpenAI's GPT model to generate personalized messages and integrates with PeopleForce API to fetch employee and holiday data.

## Features

- **Birthday Wishes**: Automatically sends birthday wishes to employees.
- **Public Holiday Notifications**: Notifies about public holidays in various locations.
- **Health Checks**: Provides endpoints to check the health and readiness of the service.
- **Scheduler**: Uses APScheduler to schedule birthday and holiday notifications.

## Technologies Used

- **Python**: Core programming language.
- **Flask**: Web framework for the application.
- **APScheduler**: Scheduler for periodic tasks.
- **SQLite**: Database for storing employee and holiday data.
- **OpenAI API**: For generating personalized messages.
- **PeopleForce API**: For fetching employee and holiday data.
- **Google Chat Webhook**: For sending messages to Google Chat.

## Installation

### Prerequisites

- Docker
- Python 3.12

### Steps

1. **Clone the repository**:

    ``` sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Set up environment variables**:
    Create a `.env` file in the project root and add the following variables:

    ``` env
    WEBHOOK_URL=<your-webhook-url>
    OPENAI_API_KEY=<your-openai-api-key>
    PEOPLE_API_KEY=<your-peopleforce-api-key>
    PEOPLEFORCE_API_URL=<your-peopleforce-api-url>
    DB_PATH=<path-to-your-database>
    LOG_LEVEL=INFO
    NOTIFY_IF_NONE=false 
    ```

3. **Build and run the Docker container**:

    ```sh
    docker build -t happy-birthday-notifier .
    docker run -d -p 8080:8080 --env-file .env happy-birthday-notifier
    ```

## Usage

### Running the Application

The application will start a Flask server on port 8080. It will also schedule jobs for sending birthday wishes and public holiday notifications based on the environment variables.

### Health Check Endpoints

- **Health Check**: `GET /health`
- **Readiness Check**: `GET /ready`
- **Ping**: `GET /ping`

### Command-Line Interface

You can also run the birthday notifier script directly:

```sh
python src/happy_birthday.py --date YYYY-MM-DD
```

## Project Structure

```.
├── Dockerfile
├── requirements.txt
├── .gitignore
├── .env.example
├── src
│   ├── main.py
│   ├── happy_birthday.py
│   ├── public_holiday.py
│   ├── openai_api.py
│   ├── peopleforce_api.py
│   ├── import_data.py
│   ├── db_functions.py
│   ├── google_space_webhook.py
│   ├── healthcheck.py
│   ├── logging_config.py
│   └── prompt_templates.py
```

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License.

## Contact

For any inquiries, please contact [roman.zhulpo@paysera.net].
