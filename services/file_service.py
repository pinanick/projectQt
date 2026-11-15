"""Импорт и экспорт CSV, сохранение простого TXT-отчёта."""
import csv
from datetime import datetime
from pathlib import Path

from config import EVENT_LABELS, INCIDENT_LABELS

COLUMNS = ("timestamp", "username", "ip", "event_type")
MAX_CSV_ROWS = 10000


def load_csv(path):
    """Проверяет CSV целиком перед добавлением событий в базу."""
    # Сначала проверяем весь файл, чтобы не добавить в БД неполные данные.
    events = []
    with open(path, "r", encoding="utf-8-sig", newline="") as file:
        # DictReader выдаёт строки по названиям столбцов CSV.
        reader = csv.DictReader(file)
        if not reader.fieldnames or not set(COLUMNS).issubset(reader.fieldnames):
            raise ValueError("CSV должен содержать: " + ", ".join(COLUMNS))
        for number, row in enumerate(reader, start=2):
            if len(events) >= MAX_CSV_ROWS:
                raise ValueError("Один файл может содержать не более 10000 событий")
            event = {key: (row.get(key) or "").strip() for key in COLUMNS}
            # Приводим формат времени к единому виду для анализа событий.
            try:
                datetime.strptime(event["timestamp"], "%Y-%m-%dT%H:%M:%S")
            except ValueError as error:
                raise ValueError(f"Строка {number}: неверное время") from error
            if not event["username"] or not event["ip"]:
                raise ValueError(f"Строка {number}: пустой пользователь или IP")
            if event["event_type"] not in EVENT_LABELS:
                raise ValueError(f"Строка {number}: неизвестный тип события")
            events.append(event)
    return events


def save_csv(path, events):
    # utf-8-sig позволяет Excel корректно открыть русский текст.
    with open(path, "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        writer.writeheader()
        for event in events:
            writer.writerow({key: event[key] for key in COLUMNS})


def save_report(path, repo):
    """Обычный текстовый отчёт, без сторонних библиотек."""
    counts = repo.get_event_counts()
    incidents = repo.get_incidents()
    rule = repo.get_rule()
    # Отчёт собирается из актуальных данных БД, а не из содержимого таблиц Qt.
    lines = [
        "CyberLab — отчёт по событиям",
        f"Сформирован: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        f"Всего событий: {counts['total']}",
        f"Ошибок входа: {counts['failed']}",
        f"Инцидентов: {len(incidents)}",
        f"Правило ошибок: {rule['threshold']} за {rule['window_seconds']} с",
        "", "Список инцидентов:",
    ]
    if not incidents:
        lines.append("Инцидентов нет")
    for incident in incidents:
        kind = INCIDENT_LABELS.get(incident["incident_type"], "Инцидент")
        lines.append(
            f"#{incident['id']} | {kind} | {incident['ip']} | "
            f"{incident['username']} | {incident['status']}"
        )
        if incident["notes"].strip():
            lines.append("Комментарий: " + incident["notes"].strip())
    # Каждая строка списка станет отдельной строкой итогового файла.
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
