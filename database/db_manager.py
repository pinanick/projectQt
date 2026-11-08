"""Подключение SQLite и создание двух таблиц проекта."""
import sqlite3
from pathlib import Path

from config import DB_PATH


class DatabaseManager:
    def __init__(self, path=DB_PATH):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(path))
        # Позволяет обращаться к столбцам как к row["ip"].
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.create_tables()

    def create_tables(self):
        # IF NOT EXISTS сохраняет историю между запусками.
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                username TEXT NOT NULL,
                ip TEXT NOT NULL,
                event_type TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT NOT NULL,
                username TEXT NOT NULL,
                first_event_id INTEGER NOT NULL,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                event_count INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'new',
                notes TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (first_event_id) REFERENCES events(id),
                UNIQUE(ip, first_event_id)
            );
        """)
        self.connection.commit()

    def close(self):
        self.connection.close()
