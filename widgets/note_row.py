from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
)

from shared.ui import set_exit_icon


class NoteRowWidget(QFrame):
    clicked = Signal(str)
    delete_requested = Signal(str)

    def __init__(self, note, parent=None):
        super().__init__(parent)
        self.setObjectName("NoteRow")
        self.note = note
        self.note_id = note["id"]
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(
            """
            QFrame#NoteRow {
                background: rgba(10, 18, 34, 0.94);
                border: 1px solid rgba(79, 70, 229, 0.18);
                border-radius: 12px;
            }
            QFrame#NoteRow:hover {
                border-color: rgba(34, 197, 94, 0.32);
                background: rgba(10, 18, 34, 0.98);
            }
            QLabel {
                border: none;
                background: transparent;
            }
            QToolButton#NoteDeleteButton {
                background: rgba(244, 63, 94, 0.96);
                border: none;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
                color: #ffffff;
                padding: 0;
                margin: 0;
            }
            QToolButton#NoteDeleteButton:hover {
                background: rgba(251, 113, 133, 0.98);
            }
            """
        )
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignVCenter)

        self.setFixedHeight(36)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.title_label = QLabel(self.note.get("title", "Untitled"))
        self.title_label.setStyleSheet("color: #f8fafc; font: 700 11px 'Segoe UI';")
        self.title_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        delete_button = QToolButton()
        delete_button.setObjectName("NoteDeleteButton")
        delete_button.setCursor(Qt.PointingHandCursor)
        delete_button.setFixedSize(36, 36)
        delete_button.setStyleSheet("margin: 0; padding: 0;")
        set_exit_icon(delete_button, "#ffffff", 13)
        delete_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        delete_button.clicked.connect(self._on_delete_clicked)

        layout.addWidget(self.title_label)
        layout.addWidget(delete_button, alignment=Qt.AlignRight | Qt.AlignVCenter)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.note_id)
        super().mousePressEvent(event)

    def update_note(self, title=None, content=None):
        if title is not None:
            self.note["title"] = title.strip() or "Untitled"
            self.title_label.setText(self.note["title"])
        if content is not None:
            content_text = str(content).strip()
            self.note["content"] = content_text
            self.preview_label.setText(content_text)
            self.preview_label.setVisible(bool(content_text))

    def _on_delete_clicked(self):
        self.delete_requested.emit(self.note_id)
