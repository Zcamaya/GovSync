from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QApplication, QComboBox, QLineEdit, QPushButton, QAbstractItemView, QWidget, QMenu
from widgets.glass_dialog import GlassDialog


class WindowStateManager:
    def __init__(self, window):
        self.window = window
        self.drag_pos = QPoint()
        self.locked = False

    def toggle_maximized(self):
        if self.window.isMaximized():
            self.window.showNormal()
            self.locked = False
        else:
            self.window.showMaximized()
            self.locked = True

    def update_lock_state(self, locked: bool):
        self.locked = locked

    def _is_interactive_widget(self, widget: QWidget | None) -> bool:
        while widget:
            # If widget is a known interactive control, prevent window dragging
            if isinstance(widget, (QComboBox, QLineEdit, QPushButton, QAbstractItemView, QMenu)):
                return True
            # If the widget belongs to a popup window (combo popup, menu), treat it as interactive
            try:
                wtype = widget.window().windowType()
                if wtype == Qt.Popup:
                    return True
            except Exception:
                pass
            widget = widget.parent()
        return False

    def mousePressEvent(self, event):
        if self.window.isMaximized() or self.locked:
            self.drag_pos = QPoint()
            return
        if event.button() == Qt.LeftButton:
            target = QApplication.widgetAt(event.globalPosition().toPoint())
            if self._is_interactive_widget(target):
                self.drag_pos = QPoint()
                return
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.window.isMaximized() or self.locked:
            return
        if event.buttons() == Qt.LeftButton and not self.drag_pos.isNull():
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
