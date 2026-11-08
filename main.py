"""Точка входа CyberLab Demo. Запуск: python main.py"""
import sys

from PyQt6.QtWidgets import QApplication

from core.event_generator import generate_events
from database.db_manager import DatabaseManager
from database.repository import Repository
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CyberLab")

    # Создаём SQLite и один общий объект для работы с данными.
    db = DatabaseManager()
    repo = Repository(db)

    # Первый запуск сразу показывает данные. При последующих они не дублируются.
    if repo.get_event_counts()["total"] == 0:
        repo.add_events(generate_events(count=40))

    window = MainWindow(repo)
    window.show()
    try:
        return app.exec()  # Цикл событий PyQt6.
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
