"""Настройки проекта и подписи событий."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "cyberlab.db"

FAILED_LOGIN_THRESHOLD = 5
FAILED_LOGIN_WINDOW_SECONDS = 60
# Дополнительный простой детектор: успешный вход после трёх ошибок.
SUCCESS_AFTER_FAILURES_THRESHOLD = 3
SUCCESS_AFTER_FAILURES_WINDOW_SECONDS = 120
MAX_VISIBLE_EVENTS = 1000

EVENT_LABELS = {
    "login_success": "Успешный вход",
    "login_failed": "Ошибка входа",
    "logout": "Выход из системы",
}

INCIDENT_LABELS = {
    "failed_logins": "Частые ошибки входа",
    "success_after_failures": "Успешный вход после ошибок",
}
