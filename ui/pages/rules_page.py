"""Настройка одного рабочего правила обнаружения."""
from PyQt6.QtWidgets import (
    QCheckBox, QFormLayout, QFrame, QLabel, QMessageBox, QPushButton,
    QSpinBox, QVBoxLayout, QWidget
)

from ui.common import page_title


# Настройка порога и временного окна одного правила.
class RulesPage(QWidget):
    # Создаёт форму настроек детектора с ограничениями значений.
    def __init__(self, repo, on_change):
        super().__init__()
        self.repo = repo
        self.on_change = on_change
        # Храним ID настраиваемого правила отдельно от его названия.
        self.rule_id = None
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(22)
        root.addLayout(page_title(
            "Правила обнаружения", "Параметры поиска частых неудачных входов с одного IP"
        ))
        panel = QFrame()
        panel.setObjectName("statCard")
        form = QFormLayout(panel)
        form.setContentsMargins(24, 24, 24, 24)
        form.setSpacing(18)
        heading = QLabel("Частые ошибки входа")
        heading.setObjectName("sectionTitle")
        form.addRow(heading)
        self.threshold = QSpinBox()
        # Пользователь может выбрать только допустимый диапазон порогов.
        self.threshold.setRange(2, 100)
        self.threshold.setSuffix(" ошибок")
        form.addRow("Порог срабатывания", self.threshold)
        self.interval = QSpinBox()
        # Ограничиваем время окна диапазоном от 5 секунд до 1 часа.
        self.interval.setRange(5, 3600)
        self.interval.setSuffix(" секунд")
        form.addRow("Временное окно", self.interval)
        # Флажок переключает активность правила, сохраняя значения порога.
        self.enabled = QCheckBox("Правило активно")
        form.addRow("", self.enabled)
        self.save = QPushButton("Сохранить правило")
        self.save.setObjectName("primaryButton")
        self.save.clicked.connect(self.save_rule)
        form.addRow("", self.save)
        root.addWidget(panel)
        hint = QLabel(
            "Пример: 5 неудачных попыток входа за 60 секунд с одного IP → тревога.\n"
            "После изменения правила повторно нажмите «Анализировать»."
        )
        hint.setObjectName("mutedText")
        hint.setWordWrap(True)
        root.addWidget(hint)
        root.addStretch(1)
        self.refresh()

    # Считывает первое правило и обновляет значения элементов формы.
    def refresh(self):
        # Текущая демка показывает только первое правило из БД.
        rules = self.repo.get_rules()
        if not rules:
            self.save.setEnabled(False)
            return
        rule = rules[0]
        # Для UPDATE понадобится именно числовой первичный ключ.
        self.rule_id = rule["id"]
        self.threshold.setValue(rule["threshold"])
        self.interval.setValue(rule["window_seconds"])
        self.enabled.setChecked(bool(rule["enabled"]))

    # Сохраняет изменения существующего правила и обновляет страницы.
    def save_rule(self):
        if self.rule_id is None:
            return
        try:
            # DAO дополнительно проверяет значения и записывает настройки в SQLite.
            self.repo.update_rule(
                self.rule_id, self.threshold.value(),
                self.interval.value(), self.enabled.isChecked()
            )
            # Обновляем страницы после изменения правил, но анализ вручную запускается отдельно.
            self.on_change()
            QMessageBox.information(self, "CyberLab", "Правило сохранено.")
        except ValueError as error:
            QMessageBox.warning(self, "Некорректные параметры", str(error))
