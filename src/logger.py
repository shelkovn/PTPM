import logging
import os, sys

log_format = "%(asctime)s | [%(levelname)-7s] | %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

# Получаем папку и собираем абсолютный путь
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(BASE_DIR, "logs", "comment_parser.log")
os.makedirs(os.path.dirname(log_path), exist_ok=True)

# Базовая настройка корневого логгера
logging.basicConfig(
    level=logging.DEBUG, # Минимальный уровень логирования (аналог MinimumLevel.Debug)
    format=log_format,
    datefmt=date_format,
    handlers=[
        logging.StreamHandler(sys.stdout),          # Настройка логирования в консоль
        logging.FileHandler(log_path, encoding="utf-8") # Настройка логирования в файл
    ]
)

logger = logging.getLogger("comment_parser")