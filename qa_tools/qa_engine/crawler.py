from __future__ import annotations

from typing import List, Dict, Any
from PySide6.QtWidgets import QApplication, QWidget, QDialog, QMainWindow, QStackedWidget, QTabWidget


class UiCrawler:
    def __init__(self, app: QApplication):
        self.app = app

    def discover(self) -> Dict[str, Any]:
        windows = []
        for widget in self.app.topLevelWidgets():
            windows.append(self._describe(widget))
        return {"windows": windows}

    def _describe(self, widget: QWidget) -> Dict[str, Any]:
        children = []
        for child in widget.findChildren(QWidget):
            if child.parent() is widget:
                children.append(self._describe(child))
        return {
            "class_name": widget.__class__.__name__,
            "object_name": widget.objectName(),
            "visible": widget.isVisible(),
            "geometry": [widget.x(), widget.y(), widget.width(), widget.height()],
            "is_dialog": isinstance(widget, QDialog),
            "is_main_window": isinstance(widget, QMainWindow),
            "is_stacked_widget": isinstance(widget, QStackedWidget),
            "is_tab_widget": isinstance(widget, QTabWidget),
            "children": children,
        }
