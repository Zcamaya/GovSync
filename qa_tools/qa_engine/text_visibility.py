from __future__ import annotations

from typing import List, Dict, Any
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QLineEdit, QComboBox, QTextEdit, QPlainTextEdit


class TextVisibilityInspector:
    def __init__(self, app: QApplication):
        self.app = app

    def inspect(self) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []

        def _check(widget, text: str):
            if not widget.isVisible():
                return
            if not text or text.strip() == "":
                findings.append({
                    "type": widget.__class__.__name__,
                    "object_name": widget.objectName(),
                    "issue": "missing text or empty text",
                    "text": text,
                })

        for widget in self.app.allWidgets():
            if isinstance(widget, QLabel):
                _check(widget, widget.text())
            elif isinstance(widget, QPushButton):
                _check(widget, widget.text())
            elif isinstance(widget, QLineEdit):
                _check(widget, widget.text())
            elif isinstance(widget, QComboBox):
                _check(widget, widget.currentText())
            elif isinstance(widget, QTextEdit):
                _check(widget, widget.toPlainText())
            elif isinstance(widget, QPlainTextEdit):
                _check(widget, widget.toPlainText())

        return findings
