"""Главное окно CyberLab. Обычные вкладки PyQt6 без оформления QSS."""

from PyQt6.QtWidgets import (
    QHBoxLayout, QMainWindow, QMessageBox, QPushButton,
    QTabWidget, QVBoxLayout, QWidget,
)

from core.event_analyzer import detect_failed_logins
from core.event_generator import generate_events
from ui.pages.dashboard_page import DashboardPage
from ui.pages.events_page import EventsPage
from ui.pages.incidents_page import IncidentsPage


class MainWindow(QMainWindow):
    def __init__(self, repo):
        super().__init__()
        self.repo = repo
        self.setWindowTitle("CyberLab — демоверсия")
        self.resize(920, 600)
        self.setMinimumSize(750, 480)
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        # В центральном виджете находятся кнопки и вкладки.
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        actions = QHBoxLayout()
        generate_button = QPushButton("Сгенерировать события")
        generate_button.clicked.connect(self.generate)
        actions.addWidget(generate_button)

        analyze_button = QPushButton("Анализировать")
        analyze_button.clicked.connect(self.analyze)
        actions.addWidget(analyze_button)
        actions.addStretch()
        layout.addLayout(actions)

        # QTabWidget сам рисует обычные вкладки, отдельное меню не нужно.
        self.tabs = QTabWidget()
        self.pages = [
            DashboardPage(self.repo),
            EventsPage(self.repo),
            IncidentsPage(self.repo, self.refresh),
        ]
        for title, page in zip(("Обзор", "События", "Инциденты"), self.pages):
            self.tabs.addTab(page, title)
        layout.addWidget(self.tabs)

        self.statusBar().showMessage("Учебная демоверсия. Используются тестовые события.")

    def show_page(self, index):
        # Индексы: 0 — обзор, 1 — события, 2 — инциденты.
        self.tabs.setCurrentIndex(index)

    def refresh(self):
        for page in self.pages:
            page.refresh()

    def generate(self):
        try:
            count = self.repo.add_events(generate_events(count=40))
            self.refresh()
            self.show_page(1)
            self.statusBar().showMessage(f"Добавлено {count} событий")
        except Exception as error:
            QMessageBox.critical(self, "Ошибка генерации", str(error))

    def analyze(self):
        try:
            # Анализатор получает записи из базы и возвращает найденные серии.
            candidates = detect_failed_logins(self.repo.get_all_events())
            created = self.repo.save_incidents(candidates)
            self.refresh()
            self.show_page(2)
            self.statusBar().showMessage(f"Новых инцидентов: {created}")
            QMessageBox.information(
                self, "Анализ завершён", f"Новых инцидентов: {created}"
            )
        except Exception as error:
            QMessageBox.critical(self, "Ошибка анализа", str(error))
