from __future__ import annotations

from typing import Dict, List, Any
from PySide6.QtWidgets import QApplication


class DpiTester:
    def __init__(self, app: QApplication):
        self.app = app

    def inspect(self) -> List[Dict[str, Any]]:
        screen = self.app.primaryScreen()
        if screen is None:
            return []
        # Use the correct Qt method names (no stray spaces)
        logical_dpi = screen.logicalDotsPerInchX()
        physical_dpi = screen.physicalDotsPerInchX()
        return [{
            "logical_dpi": logical_dpi,
            "physical_dpi": physical_dpi,
        }]
