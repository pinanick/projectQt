"""Анализ синтетических событий. Здесь нет SQL и интерфейса PyQt6."""
from collections import defaultdict, deque
from datetime import datetime

from config import (
    FAILED_LOGIN_THRESHOLD, FAILED_LOGIN_WINDOW_SECONDS,
    SUCCESS_AFTER_FAILURES_THRESHOLD, SUCCESS_AFTER_FAILURES_WINDOW_SECONDS,
)


def detect_failed_logins(events, threshold=FAILED_LOGIN_THRESHOLD,
                         window_seconds=FAILED_LOGIN_WINDOW_SECONDS):
    """Находит серии ошибок с одного IP в пределах временного окна."""
    # Собираем только ошибки входа, отдельно для каждого IP.
    grouped = defaultdict(list)
    for event in events:
        if event["event_type"] == "login_failed":
            grouped[event["ip"]].append(event)

    found = []
    for ip, ip_events in grouped.items():
        # deque хранит события текущего окна от старых к новым.
        ordered = sorted(ip_events, key=lambda e: (e["timestamp"], e["id"]))
        window = deque()
        active = False

        for event in ordered:
            current = datetime.fromisoformat(event["timestamp"])
            # Слева в deque лежат самые старые события.
            while window and (current - window[0][0]).total_seconds() > window_seconds:
                window.popleft()
            window.append((current, event))

            # Серию можно зарегистрировать повторно, только если окно снова стало короче порогового значения.
            
            if len(window) < threshold:
                active = False
                continue
            if active:
                continue  # Не создаёт тревогу на каждую следующую ошибку серии.

            first_time, first_event = window[0]
            found.append({
                "incident_type": "failed_logins",
                "ip": ip,
                "username": event["username"],
                "first_event_id": first_event["id"],
                "first_seen": first_time.isoformat(timespec="seconds"),
                "last_seen": current.isoformat(timespec="seconds"),
                "event_count": len(window),
            })
            active = True
    return found


def detect_success_after_failures(events):
    """Находит успешный вход после минимум трёх ошибок того же IP и логина."""
    # Здесь важно совпадение и IP, и имени пользователя.
    grouped = defaultdict(list)
    for event in events:
        key = (event["ip"], event["username"])
        grouped[key].append(event)

    found = []
    for (ip, username), ip_events in grouped.items():
        ordered = sorted(ip_events, key=lambda e: (e["timestamp"], e["id"]))
        failures = deque()
        for event in ordered:
            current = datetime.fromisoformat(event["timestamp"])
            while failures and (
                current - failures[0][0]
            ).total_seconds() > SUCCESS_AFTER_FAILURES_WINDOW_SECONDS:
                failures.popleft()

            if event["event_type"] == "login_failed":
                failures.append((current, event))
            elif event["event_type"] == "login_success":
                # Успех проверяется только по предшествующим ошибкам в окне.
                if len(failures) >= SUCCESS_AFTER_FAILURES_THRESHOLD:
                    # ID успешного входа выступает уникальным ключом этой тревоги.
                    found.append({
                        "incident_type": "success_after_failures",
                        "ip": ip,
                        "username": username,
                        "first_event_id": event["id"],
                        "first_seen": failures[0][0].isoformat(timespec="seconds"),
                        "last_seen": current.isoformat(timespec="seconds"),
                        "event_count": len(failures) + 1,
                    })
                failures.clear()  # После успеха начинается новая серия ошибок.
    return found
