"""Общие вспомогательные функции для таблиц и подписей."""

from PyQt6.QtWidgets import (
    QAbstractItemView, QHeaderView, QLabel,
    QTableWidget, QTableWidgetItem, QVBoxLayout,
)


def create_table(columns, stretch_column=None):
    table = QTableWidget()
    table.setColumnCount(len(columns))
    table.setHorizontalHeaderLabels(columns)
    # Строки можно выбирать, но нельзя редактировать прямо в таблице.
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    table.horizontalHeader().setSectionResizeMode(
        QHeaderView.ResizeMode.ResizeToContents
    )
    if stretch_column is not None:
        table.horizontalHeader().setSectionResizeMode(
            stretch_column, QHeaderView.ResizeMode.Stretch
        )
    return table


def page_title(text, description):
    # Обычные QLabel.
    layout = QVBoxLayout()
    layout.addWidget(QLabel(text))
    layout.addWidget(QLabel(description))
    return layout


def make_item(value, color=None):
    # color оставлен для совместимости со страницами событий и инцидентов.
    return QTableWidgetItem(str(value))
