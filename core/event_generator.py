"""Безопасные синтетические данные для демонстрации SOC."""
import random
from datetime import datetime, timedelta


# Создаёт список учебных событий без сетевых запросов и доступа к ОС.
def generate_events(count=40):
    """Обычные логи и гарантированная серия из 8 ошибок с успешным входом.

    Никакие запросы в сеть не отправляются. События полностью вымышлены.
    """
    now = datetime.now().replace(microsecond=0)
    users = ["alice", "bob", "charlie", "diana", "operator"]
    ip_pool = [f"192.168.1.{i}" for i in range(10, 24)]
    # Каждый лог хранится как словарь из четырёх полей.
    events = []

    # Вначале создаём случайный фон, похожий на обычный журнал входов.
    for _ in range(count):
        when = now - timedelta(seconds=random.randint(100, 3900))
        events.append({
            "timestamp": when.isoformat(timespec="seconds"),
            "username": random.choice(users),
            "ip": random.choice(ip_pool),
            # Выбор с весами: 73% успех, 17% ошибка, 10% выход.
            "event_type": random.choices(
                ["login_success", "login_failed", "logout"],
                weights=[73, 17, 10]
            )[0],
        })

    # Отдельный IP нужен, чтобы в каждой демонстрации находилась тревога.
    simulated_ip = f"10.0.{random.randint(1, 254)}.{random.randint(1, 254)}"
    # Добавляем 8 близких по времени ошибок, чтобы сработало стандартное правило 5/60.
    for i in range(8):
        when = now - timedelta(seconds=80 - 5 * i)
        events.append({
            "timestamp": when.isoformat(timespec="seconds"),
            "username": "admin",
            "ip": simulated_ip,
            "event_type": "login_failed",
        })

    # Успех после ошибок нужен для проверки второго типа детектора.
    events.append({
        "timestamp": (now - timedelta(seconds=40)).isoformat(timespec="seconds"),
        "username": "admin",
        "ip": simulated_ip,
        "event_type": "login_success",
    })

    # Возвращаем события по времени. Их сохранением займётся Repository.
    return sorted(events, key=lambda event: event["timestamp"])
