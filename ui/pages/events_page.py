"""Журнал событий. Поля и таблица создаются из events_page.ui."""
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget

from config import BASE_DIR, EVENT_LABELS, MAX_VISIBLE_EVENTS
from ui.common import configure_table, make_item


class EventsPage(QWidget):
    def __init__(self, repo):
        super().__init__()
        self.repo = repo
        self.rows = []
        uic.loadUi(str(BASE_DIR / "ui" / "designer" / "events_page.ui"), self)
        configure_table(self.table, 4)

        self.kind.addItem("Все события", "all")
        for key, label in EVENT_LABELS.items():
            self.kind.addItem(label, key)
        self.search.textChanged.connect(self.apply_filter)
        self.kind.currentIndexChanged.connect(self.apply_filter)

    def refresh(self):
        self.rows = self.repo.get_events(limit=MAX_VISIBLE_EVENTS)
        self.apply_filter()

    def apply_filter(self, *_):
        query = self.search.text().strip().casefold()
        event_type = self.kind.currentData()
        filtered = [
            event for event in self.rows
            if (event_type == "all" or event["event_type"] == event_type)
            and (not query or query in event["username"].casefold()
                 or query in event["ip"].casefold())
        ]
        self.table.setRowCount(len(filtered))
        for i, event in enumerate(filtered):
            columns = [
                event["id"], event["timestamp"].replace("T", " "),
                event["username"], event["ip"],
                EVENT_LABELS.get(event["event_type"], event["event_type"]),
            ]
            for j, value in enumerate(columns):
                self.table.setItem(i, j, make_item(value))
        self.counter.setText(
            f"Показано: {len(filtered)} из {len(self.rows)} последних событий"
        )
