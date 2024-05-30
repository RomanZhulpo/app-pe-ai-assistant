import sys
from pathlib import Path

# Установка корневого пути проекта
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))