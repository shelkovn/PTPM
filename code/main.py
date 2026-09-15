import logging
import sys
import os
import math

# Шаблон строки лога (аналог template в Serilog)
# Содержит: время, уровень (до 7 символов для выравнивания), имя логгера и сообщение
log_format = "%(asctime)s | [%(levelname)-7s] | %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

# Получаем папку и собираем абсолютный путь
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(BASE_DIR, "Logs", "triangles.log")
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

#logging.info("Логгер успешно сконфигурирован")
#logging.info("Приложение запущено")

logger = logging.getLogger("TriangleApp")

def calculate_triangle(str_a: str, str_b: str, str_c: str):
    params_info = f"params: A='{str_a}', B='{str_b}', C='{str_c}'"
    
    # validate types
    try:
        a = float(str_a)
        b = float(str_b)
        c = float(str_c)
    except Exception:
        logger.error(f"Failed. Invalid values. {params_info}", exc_info=True)
        return "", [(-2, -2)] * 3

    # validate lengths
    if a <= 0 or b <= 0 or c <= 0 or (a + b <= c) or (a + c <= b) or (b + c <= a):
        logger.warning(f"Failed. Not a triangle. {params_info}")
        return "не треугольник", [(-1, -1)] * 3

    # determine type
    if a == b == c:
        triangle_type = "равносторонний"
    elif a == b or b == c or a == c:
        triangle_type = "равнобедренный"
    else:
        triangle_type = "разносторонний"

    # find coordinates (idk i forgor math this was llms formula if this is wrong im sorry mister pythagor)
    x1, y1 = 0.0, 0.0
    x2, y2 = a, 0.0
    x3 = (a**2 + c**2 - b**2) / (2 * a)
    y3 = math.sqrt(max(0.0, c**2 - x3**2)) #i think it puts down AB horizontally at y=0 and then finds C based off some trigonometry idk

    # scale and center
    min_x, max_x = min(x1, x2, x3), max(x1, x2, x3) 
    min_y, max_y = min(y1, y2, y3), max(y1, y2, y3)
    
    width = max_x - min_x #find rect dimensions 
    height = max_y - min_y

    #scale to canvas
    canvas_size = 100.0
    max_side = max(width, height)
    scale = canvas_size / max_side if max_side > 0 else 1.0

    # offset for centering
    offset_x = (canvas_size - width * scale) / 2 - min_x * scale
    offset_y = (canvas_size - height * scale) / 2 - min_y * scale

    coords = [
        (round(x1 * scale + offset_x), round(y1 * scale + offset_y)),
        (round(x2 * scale + offset_x), round(y2 * scale + offset_y)),
        (round(x3 * scale + offset_x), round(y3 * scale + offset_y))
    ]

    logger.info(f"Success. {params_info} | Type: {triangle_type}, Coordinates: {coords}")
    return triangle_type, coords


if __name__ == "__main__":
    logger.info("Приложение запущено")
    
    #testing
    calculate_triangle("3", "4", "5")   # [INFO   ] | Success. params: A='3', B='4', C='5' | Type: разносторонний, Coordinates: [(12, 0), (88, 0), (88, 100)]
    calculate_triangle("10", "1", "1")  # [WARNING] | Failed. Not a triangle. params: A='10', B='1', C='1'
    calculate_triangle("abc", "4", "5") # [ERROR  ] | Failed. Invalid values. params: A='abc', B='4', C='5'