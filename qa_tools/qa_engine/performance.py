from __future__ import annotations

from typing import List, Dict, Any
from PySide6.QtWidgets import QApplication, QWidget


class PerformanceInspector:
    def __init__(self, app: QApplication):
        self.app = app

    def inspect(self) -> List[Dict[str, Any]]:
        findings = []
        for widget in self.app.allWidgets():
            if isinstance(widget, QWidget):
                findings.append({
                    "class": widget.__class__.__name__,
                    "object_name": widget.objectName(),
                    "visible": widget.isVisible(),
                    "children": len(widget.findChildren(QWidget)),
                })
        return findings
