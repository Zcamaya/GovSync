from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
)


class ActivityRowWidget(QFrame):
    clicked = Signal(str, object, int)
    checked_changed = Signal(str, object, int, bool)

    def __init__(self, name, due_date, days_left, checked, parent=None):
        super().__init__(parent)
        self.setObjectName("ActivityRow")
        self.name = name
        self.due_date = due_date
        self.days_left = due_left = days_left
        self.checked = checked
        self.setCursor(Qt.PointingHandCursor)
        self._init_ui()

    def _init_ui(self):
        self.setFixedHeight(52)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(self.checked)
        self.checkbox.setCursor(Qt.PointingHandCursor)
        self.checkbox.setStyleSheet(self._checkbox_stylesheet())
        self.checkbox.toggled.connect(self._on_checkbox_toggled)
        self.checkbox.setFixedSize(18, 18)

        self.title_label = QLabel(self.name)
        self.title_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.title_label.setStyleSheet("color: #f8fafc;")

        self.detail_label = QLabel(self._detail_text())
        self.detail_label.setFont(QFont("Segoe UI", 8))
        self.detail_label.setStyleSheet("color: #94a3b8;")

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(1)
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.detail_label)

        layout.addWidget(self.checkbox, alignment=Qt.AlignTop)
        layout.addLayout(text_layout, stretch=1)

        self._update_style()

    def _checkbox_stylesheet(self):
        return """
            QCheckBox {
                border: none;
                background: transparent;
                spacing: 0;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
                border-radius: 5px;
                border: 1px solid rgba(148, 163, 184, 0.55);
                background: rgba(15, 23, 42, 0.84);
            }
            QCheckBox::indicator:hover {
                border-color: #3b82f6;
            }
            QCheckBox::indicator:checked {
                background: #3b82f6;
                border-color: #3b82f6;
            }
        """

    def _update_style(self):
        color = self._due_color()
        accent = "#3b82f6" if self.checked else color["accent"]
        border = "rgba(59, 130, 246, 0.42)" if self.checked else color["border"]
        background = "rgba(15, 23, 42, 0.78)" if self.checked else "rgba(8, 16, 34, 0.72)"

        self.setStyleSheet(f"""
            QFrame#ActivityRow {{
                background: {background};
                border: 1px solid rgba(148, 163, 184, 0.18);
                border-left: 4px solid {accent};
                border-radius: 14px;
            }}
            QLabel {{
                border: none;
                background: transparent;
            }}
        """)
        self.title_label.setStyleSheet("color: #f8fafc;" if not self.checked else "color: #bfdbfe;")
        self.detail_label.setStyleSheet(f"color: {color['text']};" if not self.checked else "color: #93c5fd;")
        self.detail_label.setText("Complete" if self.checked else self._detail_text())

    def _detail_text(self):
        if self.checked:
            return "Complete"
        if self.days_left < 0:
            return f"{abs(self.days_left)} day(s) overdue"
        if self.days_left == 0:
            return "due today"
        return f"due in {self.days_left} day(s)"

    def _due_color(self):
        if self.days_left < 0:
            return {
                "accent": "#ef4444",
                "border": "rgba(239, 68, 68, 0.35)",
                "text": "#fecaca",
            }
        if self.days_left <= 3:
            return {
                "accent": "#f43f5e",
                "border": "rgba(244, 63, 94, 0.36)",
                "text": "#fecdd3",
            }
        if self.days_left <= 7:
            return {
                "accent": "#f59e0b",
                "border": "rgba(245, 158, 11, 0.32)",
                "text": "#fde68a",
            }
        return {
                "accent": "#10b981",
                "border": "rgba(16, 185, 129, 0.28)",
                "text": "#a7f3d0",
            }

    def _on_checkbox_toggled(self, checked):
        self.checked = checked
        self._update_style()
        self.checked_changed.emit(self.name, self.due_date, self.days_left, checked)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.name, self.due_date, self.days_left)
        super().mousePressEvent(event)
