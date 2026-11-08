"""Основные настройки учебного приложения."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "cyberlab.db"

# Один фиксированный детектор .
FAILED_LOGIN_THRESHOLD = 5
FAILED_LOGIN_WINDOW_SECONDS = 60
MAX_VISIBLE_EVENTS = 1000

EVENT_LABELS = {
    "login_success": "Успешный вход",
    "login_failed": "Ошибка входа",
    "logout": "Выход из системы",
}
