from PySide6.QtCore import QPoint, Qt
from widgets.glass_dialog import GlassDialog


class WindowStateManager:
    def __init__(self, window):
        self.window = window
        self.drag_pos = QPoint()

    def toggle_maximized(self):
        if self.window.isMaximized():
            self.window.showNormal()
        else:
            self.window.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            next_pos = self.window.pos() + event.globalPosition().toPoint() - self.drag_pos
            self.window.move(next_pos)
            self.drag_pos = event.globalPosition().toPoint()

    def closeEvent(self, event):
        dialog = GlassDialog(
            self.window,
            "Exit Application",
            "Are you sure you want to quit?",
            buttons=[
                ("No", lambda: dialog.reject(), False),
                ("Yes", lambda: dialog.accept(), True),
            ],
        )

        if dialog.exec() == GlassDialog.Accepted:
            event.accept()
        else:
            event.ignore()
