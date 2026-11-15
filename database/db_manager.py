"""Подключение SQLite и создание таблиц CyberLab."""
import sqlite3
from pathlib import Path

from config import DB_PATH, FAILED_LOGIN_THRESHOLD, FAILED_LOGIN_WINDOW_SECONDS


class DatabaseManager:
    def __init__(self, path=DB_PATH):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(path))
        # sqlite3.Row позволяет читать поля по имени, например row["ip"].
        self.connection.row_factory = sqlite3.Row
        # Проверка внешних ключей не даст сослаться на отсутствующее событие.
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.create_tables()

    def create_tables(self):
        # IF NOT EXISTS позволяет повторно открывать базу без потери данных.
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
                incident_type TEXT NOT NULL DEFAULT 'failed_logins',
                FOREIGN KEY (first_event_id) REFERENCES events(id),
                UNIQUE(ip, first_event_id)
            );
            CREATE TABLE IF NOT EXISTS rules (
                id INTEGER PRIMARY KEY CHECK(id = 1),
                threshold INTEGER NOT NULL,
                window_seconds INTEGER NOT NULL
            );
        """)
        # Обновление старой БД --- сохраняется все уже созданные инциденты.
        columns = [row[1] for row in self.connection.execute(
            "PRAGMA table_info(incidents)"
        )]
        if "incident_type" not in columns:
            self.connection.execute("""
                ALTER TABLE incidents ADD COLUMN incident_type TEXT
                NOT NULL DEFAULT 'failed_logins'
            """)
        # Первое правило создаётся один раз. Настройки пользователя сохраняются.
        self.connection.execute("""
            INSERT OR IGNORE INTO rules(id, threshold, window_seconds)
            VALUES (1, ?, ?)
        """, (FAILED_LOGIN_THRESHOLD, FAILED_LOGIN_WINDOW_SECONDS))
        self.connection.commit()

    def close(self):
        self.connection.close()
