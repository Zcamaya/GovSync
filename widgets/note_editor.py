import re

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QFont, QTextCursor, QTextListFormat
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
)

from constants.styles import AppStyles
from shared.ui import set_exit_icon


class RichNotesEditor(QTextEdit):
    def keyPressEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            key = event.key()
            if key == Qt.Key_B:
                self._toggle_format("bold")
                return
            if key == Qt.Key_I:
                self._toggle_format("italic")
                return
            if key == Qt.Key_U:
                self._toggle_format("underline")
                return

        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            cursor = self.textCursor()
            if cursor.currentList() is not None:
                super().keyPressEvent(event)
                cursor = self.textCursor()
                if cursor.currentList() is not None and not cursor.block().text().strip():
                    return
                return

        super().keyPressEvent(event)

    def _toggle_format(self, mode):
        if mode == "bold":
            self.setFontWeight(QFont.Normal if self.fontWeight() == QFont.Bold else QFont.Bold)
        elif mode == "italic":
            self.setFontItalic(not self.fontItalic())
        elif mode == "underline":
            self.setFontUnderline(not self.fontUnderline())


class NoteEditorDialog(QDialog):
    title_changed = Signal(str)
    content_changed = Signal(str)

    def __init__(self, note, parent=None):
        super().__init__(parent)
        self.note = note
        self.setWindowTitle("Note Editor")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        self.setMinimumSize(640, 500)
        self.drag_pos = QPoint()
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(AppStyles.DIALOG_BASE)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(1, 1, 1, 1)
        outer.setSpacing(0)

        card = QFrame()
        card.setObjectName("DialogCard")
        outer.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(AppStyles.SECTION_PADDING, AppStyles.INNER_PADDING, AppStyles.SECTION_PADDING, AppStyles.INNER_PADDING)
        layout.setSpacing(AppStyles.INNER_PADDING)

        title_row = QHBoxLayout()
        title_row.setSpacing(10)
        close_btn = QPushButton()
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(Qt.PointingHandCursor)
        set_exit_icon(close_btn, "#ffffff", 11)
        close_btn.clicked.connect(self.reject)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #ef4444;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: #f87171;
            }
        """)
        title = QLabel("Edit Note")
        title.setObjectName("DialogTitle")
        title_row.addStretch()
        title_row.addWidget(title)
        title_row.addStretch()
        title_row.addWidget(close_btn, alignment=Qt.AlignRight)
        layout.addLayout(title_row)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Title")
        self.title_input.setText(self.note.get("title", ""))
        self.title_input.textChanged.connect(
            lambda text: self.title_changed.emit(text)
        )
        layout.addWidget(self.title_input)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(6)
        for label, callback in [
            ("B", lambda: self._toggle_editor("bold")),
            ("I", lambda: self._toggle_editor("italic")),
            ("U", lambda: self._toggle_editor("underline")),
            ("Bullets", lambda: self._insert_list(QTextListFormat.ListDisc)),
        ]:
            button = QToolButton()
            button.setText(label)
            button.clicked.connect(callback)
            if label == "Bullets":
                button.setMinimumWidth(58)
            toolbar.addWidget(button)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.content_input = RichNotesEditor()
        self.content_input.setAcceptRichText(True)
        self.content_input.setHtml(self.note.get("content", ""))
        self.content_input.textChanged.connect(
            lambda: self.content_changed.emit(self.content_input.toHtml())
        )
        layout.addWidget(self.content_input, stretch=1)

        actions = QHBoxLayout()
        actions.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save")
        save_btn.setObjectName("PrimaryButton")
        save_btn.clicked.connect(self.accept)
        cancel_btn.setFixedHeight(38)
        save_btn.setFixedHeight(38)
        actions.addWidget(cancel_btn)
        actions.addWidget(save_btn)
        layout.addLayout(actions)

    def _toggle_editor(self, mode):
        editor = self.content_input
        if mode == "bold":
            editor.setFontWeight(QFont.Normal if editor.fontWeight() == QFont.Bold else QFont.Bold)
        elif mode == "italic":
            editor.setFontItalic(not editor.fontItalic())
        elif mode == "underline":
            editor.setFontUnderline(not editor.fontUnderline())

    def _insert_list(self, style):
        cursor = self.content_input.textCursor()
        cursor.beginEditBlock()
        list_format = QTextListFormat()
        list_format.setStyle(style)
        cursor.createList(list_format)
        cursor.endEditBlock()
        self.content_input.setTextCursor(cursor)

    def get_note_state(self):
        return {
            "id": self.note["id"],
            "title": self.title_input.text().strip() or "Untitled",
            "content": self.content_input.toHtml(),
        }

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and not self.drag_pos.isNull():
            next_pos = self.pos() + event.globalPosition().toPoint() - self.drag_pos
            self.move(next_pos)
            self.drag_pos = event.globalPosition().toPoint()
        super().mouseMoveEvent(event)
