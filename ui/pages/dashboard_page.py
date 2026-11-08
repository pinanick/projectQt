"""Простая сводка по сохранённым событиям."""

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from config import EVENT_LABELS
from ui.common import create_table, make_item


class DashboardPage(QWidget):
    def __init__(self, repo):
        super().__init__()
        self.repo = repo
        layout = QVBoxLayout(self)

        # Сводку показываем обычными надписями.
        self.total_label = QLabel()
        self.failed_label = QLabel()
        self.incidents_label = QLabel()
        layout.addWidget(self.total_label)
        layout.addWidget(self.failed_label)
        layout.addWidget(self.incidents_label)

        layout.addWidget(QLabel("Последние события:"))
        self.table = create_table(["Время", "Пользователь", "IP", "Событие"], 3)
        layout.addWidget(self.table)
        layout.addWidget(QLabel("Все события в этой версии искусственные."))

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
