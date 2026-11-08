"""Поиск подозрительных серий ошибок входа методом скользящего окна."""
from collections import defaultdict, deque
from datetime import datetime

from config import FAILED_LOGIN_THRESHOLD, FAILED_LOGIN_WINDOW_SECONDS


def detect_failed_logins(events):
    """Возвращает инциденты: >=5 ошибок от одного IP за 60 секунд.

    Здесь нет SQL и PyQt: функция только принимает события и анализирует их.
    Одна непрерывная серия ошибок создаёт один кандидат на инцидент.
    """
    grouped = defaultdict(list)
    for event in events:
        if event["event_type"] == "login_failed":
            grouped[event["ip"]].append(event)

    found = []
    for ip, ip_events in grouped.items():
        # Сортируем по времени; id разрешает совпадающие временные метки.
        ordered = sorted(ip_events, key=lambda e: (e["timestamp"], e["id"]))
        window = deque()
        active = False

        for event in ordered:
            current = datetime.fromisoformat(event["timestamp"])
            # Убираем ошибки, которые уже не входят в 60-секундное окно.
            while window and (current - window[0][0]).total_seconds() > FAILED_LOGIN_WINDOW_SECONDS:
                window.popleft()
            window.append((current, event))

            if len(window) < FAILED_LOGIN_THRESHOLD:
                active = False
                continue
            if active:
                continue  # В той же серии не создаём новую тревогу.

            first_time, first_event = window[0]
            found.append({
                "ip": ip,
                "username": event["username"],
                "first_event_id": first_event["id"],
                "first_seen": first_time.isoformat(timespec="seconds"),
                "last_seen": current.isoformat(timespec="seconds"),
                "event_count": len(window),
            })
            active = True

    return found
