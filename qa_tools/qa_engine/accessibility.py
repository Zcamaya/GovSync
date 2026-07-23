from __future__ import annotations

from typing import List, Dict, Any
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QComboBox, QLabel


class AccessibilityInspector:
    def __init__(self, app: QApplication):
        self.app = app

    def inspect(self) -> List[Dict[str, Any]]:
        findings = []
        for widget in self.app.allWidgets():
            if isinstance(widget, QLineEdit):
                focusable = widget.focusPolicy() != Qt.NoFocus
                findings.append({"type": "line_edit", "object_name": widget.objectName(), "focusable": focusable})
            elif isinstance(widget, QPushButton):
                findings.append({"type": "button", "text": widget.text(), "object_name": widget.objectName(), "enabled": widget.isEnabled()})
            elif isinstance(widget, QComboBox):
                findings.append({"type": "combo_box", "object_name": widget.objectName(), "enabled": widget.isEnabled()})
            elif isinstance(widget, QLabel):
                findings.append({"type": "label", "text": widget.text(), "object_name": widget.objectName()})
        return findings
