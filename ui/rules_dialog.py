"""Окно настройки правила обнаружения. Макет хранится в rules_dialog.ui."""
from PyQt6 import uic
from PyQt6.QtWidgets import QDialog

from config import BASE_DIR


class RulesDialog(QDialog):
    def __init__(self, repo, parent=None):
        super().__init__(parent)
        self.repo = repo
        uic.loadUi(str(BASE_DIR / "ui" / "designer" / "rules_dialog.ui"), self)
        rule = repo.get_rule()
        self.threshold.setValue(rule["threshold"])
        self.window_seconds.setValue(rule["window_seconds"])
        self.buttons.accepted.connect(self.save)
        self.buttons.rejected.connect(self.reject)

    def save(self):
        self.repo.update_rule(self.threshold.value(), self.window_seconds.value())
        self.accept()
