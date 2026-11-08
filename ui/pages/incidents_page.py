"""Просмотр и управление карточкой инцидента."""
from PyQt6.QtWidgets import (
    QComboBox, QFormLayout, QHBoxLayout, QLabel, QMessageBox, QPlainTextEdit,
    QPushButton, QVBoxLayout, QWidget
)

from ui.common import create_table, make_item, page_title

STATUS_OPTIONS = [
    ("Новый", "new"), ("Расследуется", "investigating"), ("Закрыт", "closed")
]
STATUS_LABELS = dict((value, label) for label, value in STATUS_OPTIONS)


# Просмотр тревог и изменение статуса/комментария расследования.
class IncidentsPage(QWidget):
    # Создаёт таблицу инцидентов, форму статуса и поле комментария.
    def __init__(self, repo, on_change):
        super().__init__()
        self.repo = repo
        # Обычный Python callback к refresh() главного окна; не отдельный pyqtSignal.
        self.on_change = on_change
        self.rows = []
        # Сохраняем ID записи БД, а не номер строки таблицы.
        self.selected_id = None
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(16)
        root.addLayout(page_title(
            "Расследование инцидентов",
            "Выберите тревогу, измените её статус и добавьте комментарий аналитика"
        ))

        self.table = create_table(
            ["ID", "IP", "Тип", "Пользователь", "Статус", "Первое событие"], 2
        )
        # Выделение строки вызывает заполнение формы подробностей.
        self.table.itemSelectionChanged.connect(self.select_incident)
        root.addWidget(self.table, 3)

        details = QWidget()
        fields = QFormLayout(details)
        fields.setSpacing(10)
        self.info = QLabel("Выберите инцидент в таблице")
        self.info.setObjectName("mutedText")
        self.info.setWordWrap(True)
        fields.addRow("Детали:", self.info)
        self.status = QComboBox()
        for label, value in STATUS_OPTIONS:
            self.status.addItem(label, value)
        fields.addRow("Статус:", self.status)
        self.notes = QPlainTextEdit()
        self.notes.setPlaceholderText("Что удалось установить при расследовании?")
        self.notes.setMaximumHeight(85)
        fields.addRow("Комментарий:", self.notes)
        buttons = QHBoxLayout()
        self.save = QPushButton("Сохранить изменения")
        self.save.setObjectName("primaryButton")
        self.save.clicked.connect(self.save_incident)
        buttons.addStretch()
        buttons.addWidget(self.save)
        root.addWidget(details, 2)
        root.addLayout(buttons)
        # До выбора инцидента форму нельзя редактировать.
        self.set_detail_enabled(False)

    # Блокирует или разрешает изменение полей карточки.
    def set_detail_enabled(self, enabled):
        self.status.setEnabled(enabled)
        self.notes.setEnabled(enabled)
        self.save.setEnabled(enabled)

    # Перечитывает инциденты и восстанавливает выбранную запись по ID.
    def refresh(self):
        # Запоминаем ID выбранного инцидента, чтобы восстановить выделение.
        previous = self.selected_id
        self.rows = self.repo.get_incidents()
        # Не вызываем select_incident по сто раз при программном заполнении строк.
        self.table.blockSignals(True)
        self.table.setRowCount(len(self.rows))
        # Значение -1 обозначает, что нужная строка пока не найдена.
        new_row = -1
        for i, incident in enumerate(self.rows):
            if incident["id"] == previous:
                new_row = i
            values = [
                incident["id"], incident["ip"], "Ошибки входа",
                incident["username"], STATUS_LABELS.get(incident["status"], "?"),
                incident["first_seen"].replace("T", " ")
            ]
            for j, value in enumerate(values):
                self.table.setItem(i, j, make_item(value))
        # Возвращаем реакцию на пользовательские выделения.
        self.table.blockSignals(False)
        # Если прежняя запись исчезла, выбираем первую доступную.
        if new_row < 0 and self.rows:
            new_row = 0
        if new_row >= 0:
            self.table.selectRow(new_row)
            self.select_incident()
        else:
            # Сохраняем ID записи БД, а не номер строки таблицы.
            self.selected_id = None
            self.info.setText("Инцидентов пока нет. Сначала проведите анализ.")
            self.notes.clear()
            # До выбора инцидента форму нельзя редактировать.
            self.set_detail_enabled(False)

    # Подставляет в форму данные выбранного инцидента.
    def select_incident(self):
        # Номер выбранной видимой строки используется для доступа к self.rows.
        row = self.table.currentRow()
        if not 0 <= row < len(self.rows):
            return
        incident = self.rows[row]
        self.selected_id = incident["id"]
        self.set_detail_enabled(True)
        self.info.setText(
            f"IP {incident['ip']} · серия ошибок входа · "
            f"{incident['event_count']} ошибок за короткий интервал · "
            f"{incident['first_seen'].replace('T', ' ')}"
        )
        # В выпадающем списке ищем машинный код статуса, а не русский текст.
        index = self.status.findData(incident["status"])
        self.status.setCurrentIndex(max(index, 0))
        self.notes.setPlainText(incident["notes"])

    # Сохраняет изменения через DAO и вызывает обновление страниц.
    def save_incident(self):
        if self.selected_id is None:
            return
        try:
            # Запись комментария и статуса выполняется только через Repository.
            self.repo.update_incident(
                self.selected_id, self.status.currentData(), self.notes.toPlainText()
            )
            # После сохранения все страницы перечитают актуальные данные.
            self.on_change()
        except (ValueError, OSError) as error:
            QMessageBox.warning(self, "Ошибка сохранения", str(error))
