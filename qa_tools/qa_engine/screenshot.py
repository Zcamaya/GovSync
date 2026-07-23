from __future__ import annotations

from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication, QWidget

from qa_tools.qa_engine.config import SCREENSHOT_DIR


class ScreenshotCapture:
    def __init__(self, app: QApplication):
        self.app = app

    def capture(self, label: str, widget: QWidget | None = None) -> Path:
        self.app.processEvents()
        target = widget
        if target is None:
            target = self.app.activeWindow()

        if target is None:
            top_levels = [w for w in self.app.topLevelWidgets() if w.isVisible() and w.size().isValid()]
            target = top_levels[0] if top_levels else None

        if target is None:
            top_levels = [w for w in self.app.topLevelWidgets() if w.size().isValid()]
            target = top_levels[0] if top_levels else None

        if target is None:
            raise RuntimeError("No window available for screenshot")

        pixmap = target.grab()
        path = SCREENSHOT_DIR / f"{label}.png"
        success = pixmap.save(str(path))
        if not success or not path.exists():
            raise RuntimeError(f"Failed to save screenshot '{path}'")
        return path
