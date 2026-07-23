from __future__ import annotations

from typing import List, Dict, Any
from PySide6.QtWidgets import QApplication, QTableWidget


class TableInspector:
    def __init__(self, app: QApplication):
        self.app = app

    def inspect(self) -> List[Dict[str, Any]]:
        findings = []
        for widget in self.app.allWidgets():
            if isinstance(widget, QTableWidget):
                findings.append({
                    "object_name": widget.objectName(),
                    "rows": widget.rowCount(),
                    "columns": widget.columnCount(),
                })
        return findings
