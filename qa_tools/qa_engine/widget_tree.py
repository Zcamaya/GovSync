from __future__ import annotations

from typing import List, Dict, Any
from PySide6.QtWidgets import QApplication, QWidget


class WidgetTreeAnalyzer:
    def __init__(self, app: QApplication):
        self.app = app

    def collect_widget_tree(self, root: QWidget | None = None) -> List[Dict[str, Any]]:
        roots = [root] if root is not None else [w for w in self.app.topLevelWidgets() if isinstance(w, QWidget)]
        nodes: List[Dict[str, Any]] = []
        for widget in roots:
            nodes.append(self._describe_widget(widget, 0))
        return nodes

    def _describe_widget(self, widget: QWidget, depth: int) -> Dict[str, Any]:
        children = []
        for child in widget.findChildren(QWidget):
            if child is widget:
                continue
            if child.parent() is widget:
                children.append(self._describe_widget(child, depth + 1))
        return {
            "type": widget.__class__.__name__,
            "object_name": widget.objectName(),
            "geometry": [widget.x(), widget.y(), widget.width(), widget.height()],
            "visible": widget.isVisible(),
            "depth": depth,
            "children": children,
        }
