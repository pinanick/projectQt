"""Общие настройки таблиц, которые создаёт Qt Designer."""
from PyQt6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidgetItem


def configure_table(table, stretch_column=None):
    # Запрещаем редактировать данные непосредственно в журнале.
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


def make_item(value):
    return QTableWidgetItem(str(value))
