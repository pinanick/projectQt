"""Главное окно CyberLab. Элементы интерфейса описаны в main_window.ui."""
from PyQt6 import uic
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from config import BASE_DIR
from core.event_analyzer import detect_failed_logins, detect_success_after_failures
from core.event_generator import generate_events
from services.file_service import load_csv, save_csv, save_report
from ui.pages.dashboard_page import DashboardPage
from ui.pages.events_page import EventsPage
from ui.pages.incidents_page import IncidentsPage
from ui.rules_dialog import RulesDialog


class MainWindow(QMainWindow):
    def __init__(self, repo):
        super().__init__()
        self.repo = repo

        # uic загружает виджеты из файла, созданного в Qt Designer.
        uic.loadUi(str(BASE_DIR / "ui" / "designer" / "main_window.ui"), self)

        # Подключаем действия к методам Python. В .ui нет алгоритмов анализа.
        self.generateButton.clicked.connect(self.generate)
        self.analyzeButton.clicked.connect(self.analyze)
        self.rulesButton.clicked.connect(self.configure_rule)
        self.actionImportCsv.triggered.connect(self.import_csv)
        self.actionExportCsv.triggered.connect(self.export_csv)
        self.actionReportTxt.triggered.connect(self.export_report)

        # Вместо пустых вкладок из макета вставляем наши страницы.
        self.tabs.clear()
        self.pages = [
            DashboardPage(self.repo),
            EventsPage(self.repo),
            IncidentsPage(self.repo, self.refresh),
        ]
        for title, page in zip(("Обзор", "События", "Инциденты"), self.pages):
            self.tabs.addTab(page, title)

        self.statusBar().showMessage("Учебная версия: используются тестовые события")
        self.refresh()

    def refresh(self):
        # После изменений в базе перечитываем данные на всех страницах.
        for page in self.pages:
            page.refresh()

    def generate(self):
        try:
            count = self.repo.add_events(generate_events(count=40))
            self.refresh()
            self.tabs.setCurrentIndex(1)
            self.statusBar().showMessage(f"Добавлено {count} событий")
        except Exception as error:
            QMessageBox.critical(self, "Ошибка генерации", str(error))

    def analyze(self):
        try:
            events = self.repo.get_all_events()
            rule = self.repo.get_rule()
            candidates = detect_failed_logins(
                events, rule["threshold"], rule["window_seconds"]
            )
            candidates += detect_success_after_failures(events)
            created = self.repo.save_incidents(candidates)
            self.refresh()
            self.tabs.setCurrentIndex(2)
            self.statusBar().showMessage(f"Новых инцидентов: {created}")
            QMessageBox.information(
                self, "Анализ завершён", f"Новых инцидентов: {created}"
            )
        except Exception as error:
            QMessageBox.critical(self, "Ошибка анализа", str(error))

    def configure_rule(self):
        dialog = RulesDialog(self.repo, self)
        if dialog.exec():
            self.statusBar().showMessage("Правило сохранено. Проведите анализ снова")

    def import_csv(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать CSV", "", "CSV (*.csv)"
        )
        if not path:
            return
        try:
            count = self.repo.add_events(load_csv(path))
            self.refresh()
            self.tabs.setCurrentIndex(1)
            QMessageBox.information(self, "Импорт", f"Загружено событий: {count}")
        except (OSError, ValueError) as error:
            QMessageBox.warning(self, "Ошибка импорта", str(error))

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить CSV", "events.csv", "CSV (*.csv)"
        )
        if path:
            try:
                save_csv(path, self.repo.get_all_events())
                self.statusBar().showMessage("CSV сохранён")
            except OSError as error:
                QMessageBox.warning(self, "Ошибка экспорта", str(error))

    def export_report(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить отчёт", "report.txt", "Текст (*.txt)"
        )
        if path:
            try:
                save_report(path, self.repo)
                self.statusBar().showMessage("Отчёт сохранён")
            except OSError as error:
                QMessageBox.warning(self, "Ошибка отчёта", str(error))
