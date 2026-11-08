"""Repository: отдельный слой запросов к SQLite для интерфейса и логики."""


class Repository:
    def __init__(self, db):
        self.connection = db.connection

    def add_events(self, events):
        # Плейсхолдеры ? безопасно подставляют значения в SQL.
        rows = [(e["timestamp"], e["username"], e["ip"], e["event_type"])
                for e in events]
        with self.connection:
            self.connection.executemany("""
                INSERT INTO events(timestamp, username, ip, event_type)
                VALUES (?, ?, ?, ?)
            """, rows)
        return len(rows)

    def get_events(self, limit=None):
        query = "SELECT * FROM events ORDER BY timestamp DESC, id DESC"
        params = ()
        if limit is not None:
            query += " LIMIT ?"
            params = (limit,)
        return [dict(row) for row in self.connection.execute(query, params)]

    def get_all_events(self):
        # Анализируем все сохранённые события, а не только видимые в таблице.
        return [dict(row) for row in self.connection.execute(
            "SELECT * FROM events ORDER BY timestamp, id"
        )]

    def get_event_counts(self):
        row = self.connection.execute("""
            SELECT COUNT(*) AS total,
                   COALESCE(SUM(CASE WHEN event_type = 'login_failed'
                               THEN 1 ELSE 0 END), 0) AS failed
            FROM events
        """).fetchone()
        return dict(row)

    def get_incidents(self):
        return [dict(row) for row in self.connection.execute(
            "SELECT * FROM incidents ORDER BY id DESC"
        )]

    def count_incidents(self):
        return self.connection.execute(
            "SELECT COUNT(*) FROM incidents"
        ).fetchone()[0]

    def save_incidents(self, incidents):
        # Ограничение UNIQUE не даёт повторно сохранить найденную серию.
        before = self.count_incidents()
        rows = [(i["ip"], i["username"], i["first_event_id"],
                 i["first_seen"], i["last_seen"], i["event_count"])
                for i in incidents]
        with self.connection:
            self.connection.executemany("""
                INSERT OR IGNORE INTO incidents(
                    ip, username, first_event_id, first_seen,
                    last_seen, event_count
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, rows)
        return self.count_incidents() - before

    def update_incident(self, incident_id, status, notes):
        if status not in ("new", "investigating", "closed"):
            raise ValueError("Неизвестный статус инцидента")
        with self.connection:
            self.connection.execute("""
                UPDATE incidents SET status = ?, notes = ? WHERE id = ?
            """, (status, notes, incident_id))
