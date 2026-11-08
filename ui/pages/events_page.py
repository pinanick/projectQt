"""Журнал и фильтрация событий."""
from PyQt6.QtWidgets import (
    QComboBox, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget
)

from config import EVENT_LABELS, MAX_VISIBLE_EVENTS
from ui.common import create_table, make_item, page_title


# Журнал событий с поиском и фильтром типов.
class EventsPage(QWidget):
    # Создаёт строку поиска, переключатель типов и таблицу.
    def __init__(self, repo):
        super().__init__()
        self.repo = repo
        # Здесь хранится  текущая загруженная выборка для фильтрации в памяти.
        self.rows = []
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(16)
        root.addLayout(page_title(
            "Журнал событий", "Поиск по пользователю или IP и фильтр типов событий"
        ))

        filters = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Поиск по IP или имени пользователя...")
        # Сигнал срабатывает при каждом изменении поискового текста.
        self.search.textChanged.connect(self.apply_filter)
        self.kind = QComboBox()
        self.kind.addItem("Все события", "all")
        for key, label in EVENT_LABELS.items():
            self.kind.addItem(label, key)
        # Изменение выпадающего списка также запускает фильтрацию.
        self.kind.currentIndexChanged.connect(self.apply_filter)
        filters.addWidget(self.search, 1)
        filters.addWidget(self.kind)
        root.addLayout(filters)

        self.table = create_table(["ID", "Время", "Пользователь", "IP", "Тип события"], 4)
        root.addWidget(self.table, 1)
        self.counter = QLabel("")
        self.counter.setObjectName("mutedText")
        root.addWidget(self.counter)

    # Повторно считывает последние события и применяет фильтр.
    def refresh(self):
        # Из БД берём максимум 1000 последних записей; анализатор читает ВСЕ.
        self.rows = self.repo.get_events(limit=MAX_VISIBLE_EVENTS)
        self.apply_filter()

    # Фильтрует считанные события в памяти и перерисовывает таблицу.
    def apply_filter(self, *_):
        # casefold позволяет сопоставлять строки без учёта регистра.
        query = self.search.text().strip().casefold()
        event_type = self.kind.currentData()
        # Списковое включение фильтрует строки, не меняя содержимое SQLite.
        filtered = [e for e in self.rows
                    if (event_type == "all" or e["event_type"] == event_type)
                    and (not query or query in e["username"].casefold()
                         or query in e["ip"].casefold())]
        # Перед заполнением изменяем число видимых строк таблицы.
        self.table.setRowCount(len(filtered))
        for i, event in enumerate(filtered):
            columns = [
                event["id"], event["timestamp"].replace("T", " "),
                event["username"], event["ip"], EVENT_LABELS[event["event_type"]]
            ]
            for j, value in enumerate(columns):
                # Красным выделяем тип события при ошибке входа.
                color = "#fca5a5" if j == 4 and event["event_type"] == "login_failed" else None
                self.table.setItem(i, j, make_item(value, color))
        self.counter.setText(f"Показано: {len(filtered)} из {len(self.rows)} последних событий")
