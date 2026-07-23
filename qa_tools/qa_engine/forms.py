from __future__ import annotations

from typing import List, Dict, Any
from PySide6.QtWidgets import QApplication, QLineEdit, QComboBox, QPushButton


class FormInspector:
    def __init__(self, app: QApplication):
        self.app = app

    def inspect(self) -> List[Dict[str, Any]]:
        findings = []
        for widget in self.app.allWidgets():
            if isinstance(widget, QLineEdit):
                findings.append({"type": "line_edit", "object_name": widget.objectName(), "text": widget.text()})
            elif isinstance(widget, QComboBox):
                findings.append({"type": "combo_box", "object_name": widget.objectName(), "count": widget.count()})
            elif isinstance(widget, QPushButton):
                findings.append({"type": "button", "text": widget.text(), "object_name": widget.objectName()})
        return findings
