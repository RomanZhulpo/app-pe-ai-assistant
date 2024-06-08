
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Define build-time arguments and set default values
ARG BIRTHDAY_HOUR=7
ARG BIRTHDAY_MINUTE=0
ARG HOLIDAY_HOUR=7
ARG HOLIDAY_MINUTE=01
ARG LOG_LEVEL=INFO
ARG DB_PATH=/app/db/app.db  # Ensure this points to a file, not a directory

# Set environment variables based on build-time arguments
ENV BIRTHDAY_HOUR=${BIRTHDAY_HOUR}
ENV BIRTHDAY_MINUTE=${BIRTHDAY_MINUTE}
ENV HOLIDAY_HOUR=${HOLIDAY_HOUR}
ENV HOLIDAY_MINUTE=${HOLIDAY_MINUTE}
ENV WEBHOOK_URL=${WEBHOOK_URL}
ENV LOG_LEVEL=${LOG_LEVEL}
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV PEOPLE_API_KEY=${PEOPLE_API_KEY}
ENV PEOPLEFORCE_API_URL=${PEOPLEFORCE_API_URL}
ENV DB_PATH=${DB_PATH}

EXPOSE 8080

CMD ["python", "src/main.py"]