from __future__ import annotations

from typing import List, Dict, Any
from PySide6.QtWidgets import QApplication, QWidget


class LayoutValidator:
    def __init__(self, app: QApplication):
        self.app = app

    def validate(self) -> List[Dict[str, Any]]:
        issues = []
        for widget in self.app.allWidgets():
            if not isinstance(widget, QWidget):
                continue
            if widget.width() <= 0 or widget.height() <= 0:
                continue
            if widget.x() < 0 or widget.y() < 0:
                issues.append({"type": "negative_geometry", "widget": widget.__class__.__name__, "object_name": widget.objectName()})
            if widget.parent() is not None and widget.geometry().right() > widget.parent().width():
                issues.append({"type": "out_of_parent", "widget": widget.__class__.__name__, "object_name": widget.objectName()})
        return issues
