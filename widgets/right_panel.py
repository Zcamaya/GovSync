import calendar as cal_lib
import json
import os
import re
import uuid
from datetime import datetime

from PySide6.QtCore import QPoint, QTimer, Qt, Signal
from PySide6.QtGui import QFont, QTextCursor, QTextListFormat
from PySide6.QtWidgets import (
    QDialog,
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QSizePolicy,
    QWidget,
)

from constants.styles import AppStyles
from widgets.glass_panel import TrueGlassPanel
from utils.account_store import account_json_path
from utils.ui_icons import set_exit_icon


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
        self._building = True
        self._setup_ui()
        self._building = False

    def _setup_ui(self):
        self.setStyleSheet(AppStyles.DIALOG_BASE)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(1, 1, 1, 1)
        outer.setSpacing(0)

        card = QFrame()
        card.setObjectName("DialogCard")
        outer.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

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


class NoteRowWidget(QFrame):
    delete_requested = Signal(str)
    clicked = Signal(str)

    def __init__(self, note, parent=None):
        super().__init__(parent)
        self.note = note
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("NoteRow")
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(AppStyles.NOTE_ROW)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 4)
        layout.setSpacing(0)
        self.setFixedHeight(44)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setAttribute(Qt.WA_StyledBackground, True)

        title_bar = QFrame()
        title_bar.setObjectName("NoteTitleBar")
        title_bar.setFixedHeight(38)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(12, 0, 0, 0)
        title_layout.setSpacing(0)

        self.title_label = QLabel(self.note.get("title", "Untitled"))
        self.title_label.setStyleSheet("color: #f8fafc; font: 800 12px 'Segoe UI';")
        self.title_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        delete_btn = QToolButton()
        delete_btn.setFixedSize(42, 38)
        delete_btn.setCursor(Qt.PointingHandCursor)
        set_exit_icon(delete_btn, "#ffffff", 14)
        delete_btn.setStyleSheet("""
            QToolButton {
                background: rgba(244, 63, 94, 0.96);
                border: none;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
                color: #ffffff;
                font: 900 18px 'Segoe UI';
            }
            QToolButton:hover {
                background: rgba(251, 113, 133, 0.98);
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.note["id"]))

        title_layout.addWidget(self.title_label, stretch=1)
        title_layout.addWidget(delete_btn, alignment=Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(title_bar)

    def _preview_text(self):
        content = self.note.get("content", "")
        stripped = re.sub(r"<style.*?>.*?</style>", " ", content, flags=re.S | re.I)
        stripped = re.sub(r"<head.*?>.*?</head>", " ", stripped, flags=re.S | re.I)
        stripped = stripped.replace("<br>", " ").replace("<p>", " ").replace("</p>", " ")
        stripped = stripped.replace("&nbsp;", " ")
        stripped = re.sub(r"<[^>]+>", " ", stripped)
        compact = " ".join(stripped.split())
        return compact[:120] + ("..." if len(compact) > 120 else "")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.note["id"])
        super().mousePressEvent(event)

    def update_note(self, title=None, content=None):
        if title is not None:
            self.note["title"] = title.strip() or "Untitled"
            self.title_label.setText(self.note["title"])
        if content is not None:
            self.note["content"] = content


class CustomReferenceCalendar(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            CustomReferenceCalendar {
                background: rgba(30, 41, 59, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 20px;
            }
            QLabel { color: #f8fafc; background: transparent; }
            QPushButton {
                background: transparent;
                color: #94a3b8;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover { color: #ffffff; }
        """)

        self.now = datetime.now()
        self.current_year = self.now.year
        self.current_month = self.now.month

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        header_layout = QHBoxLayout()
        self.lbl_month_year = QLabel()
        self.lbl_month_year.setFont(QFont("Segoe UI", 11, QFont.Bold))

        btn_prev = QPushButton("<")
        btn_prev.setFixedSize(20, 20)
        btn_prev.clicked.connect(lambda: self.change_month(-1))

        btn_next = QPushButton(">")
        btn_next.setFixedSize(20, 20)
        btn_next.clicked.connect(lambda: self.change_month(1))

        header_layout.addWidget(btn_prev)
        header_layout.addWidget(self.lbl_month_year, alignment=Qt.AlignCenter)
        header_layout.addWidget(btn_next)

        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(5)

        layout.addLayout(header_layout)
        layout.addWidget(self.grid_container)
        self.rebuild_calendar()

    def change_month(self, delta):
        self.current_month += delta

        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        elif self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1

        self.rebuild_calendar()

    def rebuild_calendar(self):
        for index in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(index).widget()
            if widget is not None:
                widget.setParent(None)

        month_label = datetime(self.current_year, self.current_month, 1).strftime("%B %Y")
        self.lbl_month_year.setText(month_label)

        for column, day_name in enumerate(["M", "T", "W", "T", "F", "S", "S"]):
            label = QLabel(day_name)
            label.setFont(QFont("Segoe UI", 8, QFont.Bold))
            label.setStyleSheet("color: #64748b;")
            label.setAlignment(Qt.AlignCenter)
            self.grid_layout.addWidget(label, 0, column)

        month_matrix = cal_lib.monthcalendar(self.current_year, self.current_month)
        for row_index, week in enumerate(month_matrix, start=1):
            for column_index, day in enumerate(week):
                if day == 0:
                    continue

                label = QLabel(str(day))
                label.setAlignment(Qt.AlignCenter)
                label.setFixedSize(25, 25)

                is_today = (
                    day == self.now.day
                    and self.current_month == self.now.month
                    and self.current_year == self.now.year
                )
                if is_today:
                    label.setStyleSheet(
                        "background-color: #f43f5e; border-radius: 12px; "
                        "color: white; font-weight: bold;"
                    )
                else:
                    label.setStyleSheet("color: #e2e8f0;")

                self.grid_layout.addWidget(label, row_index, column_index)


class RightPanelWidget(QWidget):
    MAX_NOTES = 30
    UNDO_SECONDS = 3
    NOTE_ROW_HEIGHT = 46
    NOTE_ROW_GAP = 3
    NOTES_VIEWPORT_HEIGHT = 150

    def __init__(self, parent=None, username="default"):
        super().__init__(parent)
        self.setFixedWidth(300)
        self.username = username
        self.state = self._load_state()
        self.pending_deletes = {}
        self.delete_notices = {}
        self.status_notices = []
        self.last_deleted_note_id = None

        right_panel_layout = QVBoxLayout(self)
        right_panel_layout.setContentsMargins(0, 0, 0, 0)
        right_panel_layout.setSpacing(14)

        self.calendar_view = CustomReferenceCalendar()

        log_card = TrueGlassPanel(border_radius=20)
        log_card_layout = QVBoxLayout(log_card)
        log_card_layout.setContentsMargins(16, 16, 16, 16)
        log_card_layout.setSpacing(12)

        log_header = QLabel("Activity Log")
        log_header.setStyleSheet(AppStyles.CARD_HEADER)

        now = datetime.now()
        self.activity_container = QWidget()
        self.activity_container.setStyleSheet("background: transparent; border: none;")
        self.activity_layout = QVBoxLayout(self.activity_container)
        self.activity_layout.setContentsMargins(0, 0, 0, 0)
        self.activity_layout.setSpacing(6)

        for task in self._monthly_tasks(now):
            self._add_activity_row(task, now)

        self.activity_layout.addStretch()

        activity_scroll = QScrollArea()
        activity_scroll.setWidgetResizable(True)
        activity_scroll.setFrameShape(QFrame.NoFrame)
        activity_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        activity_scroll.setWidget(self.activity_container)
        activity_scroll.setStyleSheet(self._scrollable_style())

        notes_card = TrueGlassPanel(border_radius=20)
        notes_layout = QVBoxLayout(notes_card)
        notes_layout.setContentsMargins(16, 16, 16, 16)
        notes_layout.setSpacing(8)

        notes_header_row = QHBoxLayout()
        notes_header_row.setContentsMargins(0, 0, 0, 0)
        notes_header_row.setSpacing(8)

        notes_header = QLabel("Notes")
        notes_header.setStyleSheet(AppStyles.CARD_HEADER)
        notes_header_row.addWidget(notes_header)
        notes_header_row.addStretch()

        self.notes_items = []
        self.note_rows = {}
        self.notes_container = QWidget()
        self.notes_container.setStyleSheet("background: transparent; border: none;")
        self.notes_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.notes_list_layout = QVBoxLayout(self.notes_container)
        self.notes_list_layout.setContentsMargins(0, 0, 0, 0)
        self.notes_list_layout.setSpacing(self.NOTE_ROW_GAP)
        self.notes_list_layout.setAlignment(Qt.AlignTop)
        self.notes_container.setMinimumHeight(self.NOTES_VIEWPORT_HEIGHT)

        notes_scroll = QScrollArea()
        notes_scroll.setWidgetResizable(True)
        notes_scroll.setFrameShape(QFrame.NoFrame)
        notes_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        notes_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        notes_scroll.setWidget(self.notes_container)
        notes_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        notes_scroll.setStyleSheet(self._scrollable_style())
        notes_scroll.setMinimumHeight(self.NOTES_VIEWPORT_HEIGHT)
        notes_scroll.setMaximumHeight(self.NOTES_VIEWPORT_HEIGHT)

        self.add_note_btn = QPushButton("+ Add Item")
        self.add_note_btn.setCursor(Qt.PointingHandCursor)
        self.add_note_btn.setMinimumSize(96, 34)
        self.add_note_btn.setToolTip("Add Item")
        self.add_note_btn.setStyleSheet(AppStyles.ACCENT_BUTTON)
        self.add_note_btn.clicked.connect(self._add_note)
        notes_header_row.addWidget(self.add_note_btn)

        log_card_layout.addWidget(log_header)
        log_card_layout.addWidget(activity_scroll, stretch=1)
        notes_layout.addLayout(notes_header_row)
        notes_layout.addWidget(notes_scroll, stretch=1)
        notes_card.setMinimumHeight(235)

        right_panel_layout.addWidget(self.calendar_view)
        right_panel_layout.addWidget(log_card, stretch=2)
        right_panel_layout.addWidget(notes_card, stretch=1)
        self._load_notes_items()

    def set_account(self, username):
        if isinstance(username, dict):
            self.username = username.get("username", "default") or "default"
        else:
            self.username = username or "default"
        self.state = self._load_state()
        self._rebuild_activity_rows()
        self._load_notes_items()

    def _rebuild_activity_rows(self):
        while self.activity_layout.count():
            item = self.activity_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        now = datetime.now()
        for task in self._monthly_tasks(now):
            self._add_activity_row(task, now)
        self.activity_layout.addStretch()

    def _monthly_tasks(self, now):
        _, last_day = cal_lib.monthrange(now.year, now.month)
        return [
            ("Philhealth", 20),
            ("HDMF", 24),
            ("SSS", last_day),
            ("HDMF Loans", 15),
            ("SSS Loans", last_day),
        ]

    def _add_activity_row(self, task, now):
        name, due_day = task
        due_date = datetime(now.year, now.month, due_day)
        days_left = (due_date.date() - now.date()).days
        color = self._due_color(days_left)
        month_key = now.strftime("%Y-%m")
        checked = self.state.get("checks", {}).get(month_key, {}).get(name, False)

        row = QFrame()
        row.setCursor(Qt.PointingHandCursor)
        self._style_activity_row(row, color, checked)
        row.mousePressEvent = lambda event, name=name, due_date=due_date, days_left=days_left: (
            self._show_activity_detail(name, due_date, days_left)
            if event.button() == Qt.LeftButton
            else None
        )

        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(9, 6, 9, 6)
        row_layout.setSpacing(7)

        checkbox = QCheckBox()
        checkbox.setChecked(checked)
        checkbox.setCursor(Qt.PointingHandCursor)
        checkbox.setStyleSheet(f"""
            QCheckBox {{
                border: none;
                background: transparent;
                spacing: 0;
            }}
            QCheckBox::indicator {{
                width: 15px;
                height: 15px;
                border-radius: 5px;
                border: 1px solid rgba(148, 163, 184, 0.55);
                background: rgba(15, 23, 42, 0.84);
            }}
            QCheckBox::indicator:hover {{
                border-color: {color["accent"]};
            }}
            QCheckBox::indicator:checked {{
                background: {color["accent"]};
                border-color: {color["accent"]};
            }}
        """)
        text_container = QWidget()
        text_container.setStyleSheet("background: transparent; border: none;")
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)

        title = QLabel(name)
        title.setFont(QFont("Segoe UI", 9, QFont.Bold))
        title.setStyleSheet("color: #f8fafc;")

        detail = QLabel(f"{due_date.strftime('%b')} {due_day} - {self._due_text(days_left)}")
        detail.setFont(QFont("Segoe UI", 8))
        self._style_activity_text(title, detail, color, checked, days_left, due_date, due_day)

        checkbox.toggled.connect(
            lambda checked_state, row=row, title=title, detail=detail,
            color=color, days_left=days_left, due_date=due_date, due_day=due_day: (
                self._save_check(month_key, name, checked_state),
                self._style_activity_row(row, color, checked_state),
                self._style_activity_text(
                    title,
                    detail,
                    color,
                    checked_state,
                    days_left,
                    due_date,
                    due_day,
                ),
            )
        )

        text_layout.addWidget(title)
        text_layout.addWidget(detail)

        row_layout.addWidget(checkbox)
        row_layout.addWidget(text_container, stretch=1)
        self.activity_layout.addWidget(row)

    def _style_activity_row(self, row, color, checked):
        accent = "#3b82f6" if checked else color["accent"]
        border = "rgba(59, 130, 246, 0.42)" if checked else color["border"]
        background = "rgba(30, 64, 175, 0.22)" if checked else "rgba(2, 6, 23, 0.38)"

        row.setStyleSheet(f"""
            QFrame {{
                background: {background};
                border: 1px solid {border};
                border-left: 4px solid {accent};
                border-radius: 9px;
            }}
            QLabel {{
                border: none;
                background: transparent;
            }}
        """)

    def _style_activity_text(self, title, detail, color, checked, days_left, due_date, due_day):
        if checked:
            title.setStyleSheet("color: #bfdbfe;")
            detail.setText("Complete")
            detail.setStyleSheet("color: #93c5fd;")
            return

        title.setStyleSheet("color: #f8fafc;")
        detail.setText(f"{due_date.strftime('%b')} {due_day} - {self._due_text(days_left)}")
        detail.setStyleSheet(f"color: {color['text']};")

    def _due_color(self, days_left):
        if days_left < 0:
            return {
                "accent": "#ef4444",
                "border": "rgba(239, 68, 68, 0.35)",
                "text": "#fecaca",
            }
        if days_left <= 3:
            return {
                "accent": "#f43f5e",
                "border": "rgba(244, 63, 94, 0.36)",
                "text": "#fecdd3",
            }
        if days_left <= 7:
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

    def _due_text(self, days_left):
        if days_left < 0:
            return f"{abs(days_left)} day(s) overdue"
        if days_left == 0:
            return "due today"
        return f"due in {days_left} day(s)"

    def _show_activity_detail(self, name, due_date, days_left):
        from widgets.glass_dialog import GlassDialog

        month_key = due_date.strftime("%Y-%m")
        is_complete = self.state.get("checks", {}).get(month_key, {}).get(name, False)
        status = "Complete" if is_complete else self._due_text(days_left)
        message = (
            f"{name}\n\n"
            f"Due date: {due_date.strftime('%B %d, %Y')}\n"
            f"Status: {status}\n\n"
            "This reminder is saved for the current account and resets with the next month."
        )
        GlassDialog(self, "Activity Details", message).exec()

    def _load_notes_items(self):
        while self.notes_list_layout.count():
            item = self.notes_list_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        raw_notes = self.state.get("notes", [])
        if isinstance(raw_notes, str):
            raw_notes = [
                {
                    "id": str(uuid.uuid4()),
                    "title": "Main Note",
                    "content": raw_notes,
                }
            ] if raw_notes.strip() else []

        normalized_notes = []
        if isinstance(raw_notes, list):
            for note in raw_notes[: self.MAX_NOTES]:
                normalized_notes.append(self._normalize_note(note))

        if (
            len(normalized_notes) == 1
            and normalized_notes[0]["title"] == "Starter Note"
            and not normalized_notes[0]["content"].strip()
        ):
            normalized_notes = []

        self.notes_items = normalized_notes
        self.state["notes"] = self.notes_items
        self.note_rows = {}

        for note in self.notes_items:
            self.notes_list_layout.addWidget(self._make_note_row(note))

        if not self.notes_items:
            placeholder = QLabel("Notes are empty")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet(
                "color: rgba(148, 163, 184, 0.72); font: 700 13px 'Segoe UI'; padding: 20px; border: 1px dashed rgba(148, 163, 184, 0.18); border-radius: 10px; background: rgba(2, 6, 23, 0.18);"
            )
            self.notes_list_layout.addWidget(placeholder)

        self._sync_notes_container_height()
        self.notes_container.updateGeometry()
        self._update_add_button_state()
        self._save_state()

    def _make_note_row(self, note):
        row = NoteRowWidget(note)
        row.clicked.connect(self._open_note_editor)
        row.delete_requested.connect(self._delete_note)
        self.note_rows[note["id"]] = row
        return row

    def _normalize_note(self, note):
        note = note if isinstance(note, dict) else {}
        return {
            "id": str(note.get("id") or uuid.uuid4()),
            "title": str(note.get("title", "")).strip() or "Untitled",
            "content": str(note.get("content", "")),
        }

    def _add_note(self):
        if len(self.notes_items) >= self.MAX_NOTES:
            self._show_status_notice(f"Maximum of {self.MAX_NOTES} notes reached.")
            self._update_add_button_state()
            return

        note = self._normalize_note({"id": str(uuid.uuid4()), "title": "New Item", "content": ""})
        self.notes_items.append(note)
        self.state["notes"] = self.notes_items
        self._save_state()
        self._load_notes_items()
        self._open_note_editor(note["id"])

    def _delete_note(self, note_id):
        if note_id in self.pending_deletes:
            return

        note_index = next(
            (idx for idx, note in enumerate(self.notes_items) if note["id"] == note_id),
            None,
        )
        note = next((item for item in self.notes_items if item["id"] == note_id), None)
        if note is None:
            return

        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda note_id=note_id: self._finalize_pending_delete(note_id))
        countdown_timer = QTimer(self)
        countdown_timer.setInterval(1000)
        countdown_timer.timeout.connect(lambda note_id=note_id: self._tick_note_countdown(note_id))

        self.pending_deletes[note_id] = {
            "note": dict(note),
            "index": note_index if note_index is not None else len(self.notes_items),
            "timer": timer,
            "countdown_timer": countdown_timer,
            "seconds_left": self.UNDO_SECONDS,
        }
        self.last_deleted_note_id = note_id
        countdown_timer.start()
        timer.start(self.UNDO_SECONDS * 1000)

        self.notes_items = [item for item in self.notes_items if item["id"] != note_id]
        self.note_rows.pop(note_id, None)
        self.state["notes"] = self.notes_items
        self._save_state()
        self._load_notes_items()
        self._show_delete_notice(note_id, note.get("title", "Item"))
        self._update_add_button_state()

    def _open_note_editor(self, note_id):
        note = next((item for item in self.notes_items if item["id"] == note_id), None)
        if note is None:
            return

        dialog = NoteEditorDialog(note, self)
        dialog.title_changed.connect(lambda value, note_id=note_id: self._sync_note_title(note_id, value))
        dialog.content_changed.connect(lambda value, note_id=note_id: self._sync_note_content(note_id, value))
        if dialog.exec() == QDialog.Accepted:
            saved_note = dialog.get_note_state()
            self._sync_note_title(note_id, saved_note["title"])
            self._sync_note_content(note_id, saved_note["content"])

    def _sync_note_title(self, note_id, title):
        for note in self.notes_items:
            if note["id"] == note_id:
                note["title"] = title.strip() or "Untitled"
                break
        row = self.note_rows.get(note_id)
        if row is not None:
            row.update_note(title=title)
        self.state["notes"] = self.notes_items
        self._save_state()

    def _sync_note_content(self, note_id, content):
        for note in self.notes_items:
            if note["id"] == note_id:
                note["content"] = content
                break
        row = self.note_rows.get(note_id)
        if row is not None:
            row.update_note(content=content)
        self.state["notes"] = self.notes_items
        self._save_state()

    def _show_delete_notice(self, note_id, note_title):
        pending = self.pending_deletes.get(note_id)
        if pending is None:
            return

        notice = self._create_delete_notice(note_id, note_title)
        self.delete_notices[note_id] = notice
        pending["notice"] = notice
        self._update_note_notice_text(note_id)
        notice.show()
        notice.raise_()
        self._position_delete_notices()

    def _refresh_delete_notice(self):
        if not self.pending_deletes:
            self.last_deleted_note_id = None
            self._update_add_button_state()
            return

        if self.last_deleted_note_id not in self.pending_deletes:
            self.last_deleted_note_id = next(reversed(self.pending_deletes))
        self._position_delete_notices()

    def _undo_pending_delete(self, note_id=None):
        note_id = note_id or self.last_deleted_note_id
        pending = self.pending_deletes.pop(note_id, None) if note_id else None
        if pending is None:
            return

        pending["timer"].stop()
        pending.get("countdown_timer").stop()
        self._remove_delete_notice(note_id)
        note = pending["note"]
        index = pending.get("index", len(self.notes_items))
        if index < 0 or index > len(self.notes_items):
            index = len(self.notes_items)

        self.notes_items.insert(index, note)
        self.state["notes"] = self.notes_items
        self._save_state()
        self._load_notes_items()
        self._refresh_delete_notice()
        self._update_add_button_state()

    def _finalize_pending_delete(self, note_id):
        pending = self.pending_deletes.pop(note_id, None)
        if pending is None:
            return
        pending.get("countdown_timer").stop()
        self._remove_delete_notice(note_id)

        if self.last_deleted_note_id == note_id:
            self.last_deleted_note_id = None

        self._refresh_delete_notice()
        self._update_add_button_state()

    def _tick_note_countdown(self, note_id):
        pending = self.pending_deletes.get(note_id)
        if pending is None:
            return

        pending["seconds_left"] = max(0, pending.get("seconds_left", 0) - 1)
        self._update_note_notice_text(note_id)
        if pending["seconds_left"] <= 0:
            pending.get("countdown_timer").stop()

    def _create_delete_notice(self, note_id, note_title):
        parent = self._notice_parent()
        notice = QFrame(parent)
        notice.setFixedHeight(44)
        notice.setStyleSheet("""
            QFrame {
                background: rgba(10, 17, 31, 0.96);
                border: 1px solid rgba(45, 212, 191, 0.24);
                border-radius: 8px;
            }
            QLabel {
                color: #e5e7eb;
                background: transparent;
                border: none;
                font: 600 11px 'Segoe UI';
            }
            QPushButton {
                background: rgba(20, 184, 166, 0.16);
                border: 1px solid rgba(20, 184, 166, 0.34);
                border-radius: 8px;
                color: #d1fae5;
                font: 800 11px 'Segoe UI';
                min-height: 28px;
                padding: 0 12px;
            }
            QPushButton:hover {
                background: rgba(20, 184, 166, 0.26);
                color: #ffffff;
            }
        """)

        layout = QHBoxLayout(notice)
        layout.setContentsMargins(12, 7, 12, 7)
        layout.setSpacing(10)
        label = QLabel()
        label.setWordWrap(True)
        button = QPushButton()
        button.clicked.connect(lambda checked=False, note_id=note_id: self._undo_pending_delete(note_id))
        layout.addWidget(label, stretch=1)
        layout.addWidget(button)

        notice.note_id = note_id
        notice.note_title = note_title
        notice.label = label
        notice.undo_button = button
        return notice

    def _update_note_notice_text(self, note_id):
        pending = self.pending_deletes.get(note_id)
        notice = self.delete_notices.get(note_id)
        if pending is None or notice is None:
            return

        title = pending["note"].get("title", "Item")
        seconds_left = max(0, pending.get("seconds_left", 0))
        notice.label.setText(f"Item removed: {title}.")
        notice.undo_button.setText(f"Undo ({seconds_left}s)" if seconds_left else "Undo")

    def _remove_delete_notice(self, note_id):
        notice = self.delete_notices.pop(note_id, None)
        if notice is not None:
            notice.hide()
            notice.deleteLater()
        self._position_delete_notices()

    def _notice_parent(self):
        window = self.window()
        if hasattr(window, "centralWidget") and window.centralWidget() is not None:
            return window.centralWidget()
        return window

    def _position_delete_notices(self):
        parent = self._notice_parent()
        margin = 16
        gap = 8
        width = min(420, max(260, parent.width() - (margin * 2)))
        x = max(margin, (parent.width() - width) // 2)
        y = parent.height() - margin

        for note_id in reversed(list(self.delete_notices.keys())):
            notice = self.delete_notices[note_id]
            y -= notice.height()
            notice.setFixedWidth(width)
            notice.move(x, max(margin, y))
            notice.raise_()
            y -= gap

        if self.status_notices:
            self._position_status_notices()

    def _show_status_notice(self, message):
        parent = self._notice_parent()
        notice = QFrame(parent)
        notice.setFixedHeight(40)
        notice.setStyleSheet("""
            QFrame {
                background: rgba(10, 17, 31, 0.96);
                border: 1px solid rgba(45, 212, 191, 0.24);
                border-radius: 8px;
            }
            QLabel {
                color: #e5e7eb;
                background: transparent;
                border: none;
                font: 700 11px 'Segoe UI';
            }
        """)
        layout = QHBoxLayout(notice)
        layout.setContentsMargins(12, 7, 12, 7)
        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        self.status_notices.append(notice)
        notice.show()
        notice.raise_()
        self._position_status_notices()
        QTimer.singleShot(2200, lambda notice=notice: self._remove_status_notice(notice))

    def _remove_status_notice(self, notice):
        if notice in self.status_notices:
            self.status_notices.remove(notice)
        notice.hide()
        notice.deleteLater()
        self._position_status_notices()

    def _position_status_notices(self):
        parent = self._notice_parent()
        margin = 16
        gap = 8
        width = min(420, max(260, parent.width() - (margin * 2)))
        x = max(margin, (parent.width() - width) // 2)
        y = parent.height() - margin

        if self.delete_notices:
            y -= (len(self.delete_notices) * (44 + gap))

        for notice in reversed(self.status_notices):
            y -= notice.height()
            notice.setFixedWidth(width)
            notice.move(x, max(margin, y))
            notice.raise_()
            y -= gap

    def _update_add_button_state(self):
        self.add_note_btn.setEnabled(len(self.notes_items) < self.MAX_NOTES)

    def _sync_notes_container_height(self):
        if not self.notes_items:
            self.notes_container.setMinimumHeight(self.NOTES_VIEWPORT_HEIGHT)
            return

        row_count = len(self.notes_items)
        content_height = (
            row_count * self.NOTE_ROW_HEIGHT
            + max(0, row_count - 1) * self.NOTE_ROW_GAP
        )
        self.notes_container.setMinimumHeight(
            max(self.NOTES_VIEWPORT_HEIGHT, content_height)
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "delete_notices") and self.delete_notices:
            self._position_delete_notices()
        if hasattr(self, "status_notices") and self.status_notices:
            self._position_status_notices()

    def _load_state(self):
        path = account_json_path(self.username, "right_panel.json")
        if not os.path.exists(path):
            return {"notes": [], "checks": {}}
        try:
            with open(path, "r", encoding="utf-8") as input_file:
                data = json.load(input_file)
        except (OSError, json.JSONDecodeError):
            return {"notes": [], "checks": {}}
        return data if isinstance(data, dict) else {"notes": [], "checks": {}}

    def _save_state(self):
        path = account_json_path(self.username, "right_panel.json")
        with open(path, "w", encoding="utf-8") as output_file:
            json.dump(self.state, output_file, indent=2)

    def _save_check(self, month_key, name, checked):
        checks = self.state.setdefault("checks", {})
        month_checks = checks.setdefault(month_key, {})
        month_checks[name] = checked
        self._save_state()

    def _scrollable_style(self):
        return """
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """ + self._scrollbar_style()

    def _scrollbar_style(self):
        return """
            QScrollBar:vertical {
                background: rgba(2, 6, 23, 0.18);
                border: none;
                border-radius: 6px;
                width: 12px;
                margin: 3px;
            }
            QScrollBar::handle:vertical {
                background: rgba(148, 163, 184, 0.46);
                border-radius: 6px;
                min-height: 24px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(20, 184, 166, 0.72);
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
                border: none;
                height: 0;
            }
            QScrollBar:horizontal {
                background: transparent;
                height: 0;
            }
        """
