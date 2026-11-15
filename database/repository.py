"""Repository: все SQL-запросы CyberLab собраны в одном классе."""


class Repository:
    def __init__(self, db):
        self.connection = db.connection

    def add_events(self, events):
        # Плейсхолдеры ? отделяют SQL-код от пользовательских значений.
        rows = [(e["timestamp"], e["username"], e["ip"], e["event_type"])
                for e in events]
        with self.connection:
            self.connection.executemany("""
                INSERT INTO events(timestamp, username, ip, event_type)
                VALUES (?, ?, ?, ?)
            """, rows)
        return len(rows)

    def get_events(self, limit=None):
        # Для журнала можно ограничить количество загружаемых строк.
        query = "SELECT * FROM events ORDER BY timestamp DESC, id DESC"
        params = ()
        if limit is not None:
            query += " LIMIT ?"
            params = (limit,)
        return [dict(row) for row in self.connection.execute(query, params)]

    def get_all_events(self):
        # Анализатору нужна вся история, поэтому здесь нет LIMIT.
        return [dict(row) for row in self.connection.execute(
            "SELECT * FROM events ORDER BY timestamp, id"
        )]

    def get_event_counts(self):
        # COUNT считает все записи, SUM отдельно подсчитывает ошибки входа.
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
        # UNIQUE(ip, first_event_id) исключает повторное создание той же тревоги.
        before = self.count_incidents()
        rows = [(i["ip"], i["username"], i["first_event_id"],
                 i["first_seen"], i["last_seen"], i["event_count"],
                 i["incident_type"])
                for i in incidents]
        # OR IGNORE пропускает инциденты, уже сохранённые при прошлом анализе.
        with self.connection:
            self.connection.executemany("""
                INSERT OR IGNORE INTO incidents(
                    ip, username, first_event_id, first_seen,
                    last_seen, event_count, incident_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, rows)
        return self.count_incidents() - before

    def update_incident(self, incident_id, status, notes):
        # Статус храним коротким кодом, а русский текст показываем в интерфейсе.
        if status not in ("new", "investigating", "closed"):
            raise ValueError("Неизвестный статус инцидента")
        with self.connection:
            self.connection.execute("""
                UPDATE incidents SET status = ?, notes = ? WHERE id = ?
            """, (status, notes, incident_id))

    def get_rule(self):
        # Для учебной демки есть одно настраиваемое правило.
        return dict(self.connection.execute(
            "SELECT threshold, window_seconds FROM rules WHERE id = 1"
        ).fetchone())

    def update_rule(self, threshold, window_seconds):
        if not 2 <= threshold <= 20 or not 10 <= window_seconds <= 600:
            raise ValueError("Недопустимые значения правила")
        with self.connection:
            self.connection.execute("""
                UPDATE rules SET threshold = ?, window_seconds = ? WHERE id = 1
            """, (threshold, window_seconds))
