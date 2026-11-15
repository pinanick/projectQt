"""Страница обзора. Макет находится в dashboard_page.ui."""
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget

from config import BASE_DIR, EVENT_LABELS
from ui.common import configure_table, make_item


class DashboardPage(QWidget):
    def __init__(self, repo):
        super().__init__()
        self.repo = repo
        uic.loadUi(str(BASE_DIR / "ui" / "designer" / "dashboard_page.ui"), self)
        configure_table(self.table, 3)

    def refresh(self):
        counts = self.repo.get_event_counts()
        self.total_label.setText(f"Всего событий: {counts['total']}")
        self.failed_label.setText(f"Ошибок входа: {counts['failed']}")
        self.incidents_label.setText(f"Инцидентов: {self.repo.count_incidents()}")

        events = self.repo.get_events(limit=7)
        self.table.setRowCount(len(events))
        for i, event in enumerate(events):
            columns = [
                event["timestamp"].replace("T", " "),
                event["username"], event["ip"],
                EVENT_LABELS.get(event["event_type"], event["event_type"]),
            ]
            for j, value in enumerate(columns):
                self.table.setItem(i, j, make_item(value))
