"""Работа с инцидентами. Макет открывается из incidents_page.ui."""
from PyQt6 import uic
from PyQt6.QtWidgets import QMessageBox, QWidget

from config import BASE_DIR, INCIDENT_LABELS
from ui.common import configure_table, make_item

STATUS_OPTIONS = [
    ("Новый", "new"), ("Расследуется", "investigating"), ("Закрыт", "closed")
]
STATUS_LABELS = {value: label for label, value in STATUS_OPTIONS}


class IncidentsPage(QWidget):
    def __init__(self, repo, on_change):
        super().__init__()
        self.repo = repo
        self.on_change = on_change
        self.rows = []
        self.selected_id = None
        uic.loadUi(str(BASE_DIR / "ui" / "designer" / "incidents_page.ui"), self)
        configure_table(self.table, 2)
        for label, value in STATUS_OPTIONS:
            self.status.addItem(label, value)
        self.table.itemSelectionChanged.connect(self.select_incident)
        self.save.clicked.connect(self.save_incident)
        self.set_detail_enabled(False)

    def set_detail_enabled(self, enabled):
        self.status.setEnabled(enabled)
        self.notes.setEnabled(enabled)
        self.save.setEnabled(enabled)

    def refresh(self):
        previous = self.selected_id
        self.rows = self.repo.get_incidents()
        self.table.blockSignals(True)
        self.table.setRowCount(len(self.rows))
        new_row = -1
        for i, incident in enumerate(self.rows):
            if incident["id"] == previous:
                new_row = i
            values = [
                incident["id"], incident["ip"],
                INCIDENT_LABELS.get(incident["incident_type"], "Неизвестный тип"),
                incident["username"], STATUS_LABELS.get(incident["status"], "?"),
                incident["first_seen"].replace("T", " "),
            ]
            for j, value in enumerate(values):
                self.table.setItem(i, j, make_item(value))
        self.table.blockSignals(False)
        if new_row < 0 and self.rows:
            new_row = 0
        if new_row >= 0:
            self.table.selectRow(new_row)
            self.select_incident()
        else:
            self.selected_id = None
            self.info.setText("Инцидентов пока нет. Сначала проведите анализ.")
            self.notes.clear()
            self.set_detail_enabled(False)

    def select_incident(self):
        row = self.table.currentRow()
        if not 0 <= row < len(self.rows):
            return
        incident = self.rows[row]
        self.selected_id = incident["id"]
        self.set_detail_enabled(True)
        self.info.setText(
            f"IP {incident['ip']} · "
            f"{INCIDENT_LABELS.get(incident['incident_type'], 'Инцидент')} · "
            f"Событий в серии: {incident['event_count']} · "
            f"{incident['first_seen'].replace('T', ' ')}"
        )
        index = self.status.findData(incident["status"])
        self.status.setCurrentIndex(max(index, 0))
        self.notes.setPlainText(incident["notes"])

    def save_incident(self):
        if self.selected_id is None:
            return
        try:
            self.repo.update_incident(
                self.selected_id, self.status.currentData(), self.notes.toPlainText()
            )
            self.on_change()
        except (ValueError, OSError) as error:
            QMessageBox.warning(self, "Ошибка сохранения", str(error))
