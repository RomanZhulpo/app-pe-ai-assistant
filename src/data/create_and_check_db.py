import os
import sys
from pathlib import Path

# Add the project root directory to the sys.path
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from src.data.db_functions import create_database

def main():
    # Создание базы данных
    create_database()
    print("Database created successfully.")

    # Проверка, что база данных и таблица созданы
    db_path = project_root / 'db' / 'pe_assistant.db'
    if db_path.exists():
        print(f"Database file exists at: {db_path}")
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Employees';")
        table_exists = cursor.fetchone()
        if table_exists:
            print("Table 'Employees' exists in the database.")
        else:
            print("Table 'Employees' does not exist in the database.")
        conn.close()
    else:
        print("Database file does not exist.")

if __name__ == "__main__":
    main()