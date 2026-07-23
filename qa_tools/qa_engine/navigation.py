from __future__ import annotations

from typing import List, Dict, Any
from PySide6.QtWidgets import QApplication, QWidget, QListWidget, QTabWidget, QStackedWidget, QPushButton


class NavigationInspector:
    def __init__(self, app: QApplication):
        self.app = app

    def discover_navigation(self) -> List[Dict[str, Any]]:
        results = []
        for widget in self.app.allWidgets():
            if isinstance(widget, QListWidget):
                results.append({
                    "type": "list_widget",
                    "object_name": widget.objectName(),
                    "rows": widget.count(),
                    "current_row": widget.currentRow(),
                })
            elif isinstance(widget, QTabWidget):
                results.append({
                    "type": "tab_widget",
                    "object_name": widget.objectName(),
                    "tabs": [widget.tabText(i) for i in range(widget.count())],
                })
            elif isinstance(widget, QStackedWidget):
                results.append({
                    "type": "stacked_widget",
                    "object_name": widget.objectName(),
                    "current_index": widget.currentIndex(),
                    "count": widget.count(),
                })
            elif isinstance(widget, QPushButton):
                if widget.text().strip():
                    results.append({
                        "type": "button",
                        "text": widget.text(),
                        "object_name": widget.objectName(),
                    })
        return results
