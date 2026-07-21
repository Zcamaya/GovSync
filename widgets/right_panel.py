import calendar as cal_lib
import uuid
from datetime import datetime

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from constants.styles import AppStyles
from widgets.activity_row import ActivityRowWidget
from widgets.custom_reference_calendar import CustomReferenceCalendar
from widgets.glass_panel import TrueGlassPanel
from widgets.note_editor import NoteEditorDialog
from widgets.note_row import NoteRowWidget
from shared.helpers.account_state import account_state_path, resolve_account_username
from shared.helpers.json_state import load_json_dict, save_json_dict
from shared.ui import set_exit_icon


class RightPanelWidget(QWidget):
    MAX_NOTES = 30
    UNDO_SECONDS = 3
    NOTE_ROW_HEIGHT = 36
    NOTE_ROW_GAP = 2
    NOTES_VIEWPORT_HEIGHT = 150

    def __init__(self, parent=None, username="default"):
        super().__init__(parent)
        self.setObjectName("RightPanelWidget")
        self.setAttribute(Qt.WA_StyledBackground, True)
        # Use a flexible width so parent splitter can control sizing
        self.setMinimumWidth(AppStyles.RIGHT_PANEL_MIN_WIDTH)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.setStyleSheet("""
            QWidget#RightPanelWidget {
                border-radius: 18px;
            }
        """)
        self.username = username
        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self._on_resize_debounced)
        self.state = self._load_state()
        self.pending_deletes = {}
        self.delete_notices = {}
        self.status_notices = []
        self.last_deleted_note_id = None
        self._calendar_width_min = 280
        self._calendar_height_min = 170
        self._calendar_height_max = 240
        self._activity_scroll_height_min = 140
        self._notes_scroll_height_min = 108

        right_panel_layout = QVBoxLayout(self)
        right_panel_layout.setContentsMargins(
            AppStyles.SECTION_PADDING,
            AppStyles.SECTION_PADDING,
            AppStyles.SECTION_PADDING,
            AppStyles.SECTION_PADDING,
        )
        right_panel_layout.setSpacing(AppStyles.PANEL_SPACING_COMPACT)

        self.calendar_view = CustomReferenceCalendar()
        self.calendar_view.setMinimumWidth(self._calendar_width_min)
        self.calendar_view.setMinimumHeight(self._calendar_height_min)
        self.calendar_view.setMaximumHeight(self._calendar_height_max)
        self.calendar_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        log_card = TrueGlassPanel(border_radius=20)
        log_card_layout = QVBoxLayout(log_card)
        log_card_layout.setContentsMargins(
            AppStyles.SECTION_PADDING,
            AppStyles.SECTION_PADDING,
            AppStyles.SECTION_PADDING,
            AppStyles.SECTION_PADDING,
        )
        log_card_layout.setSpacing(AppStyles.INNER_PADDING - 2)

        log_header = QLabel("Activity Log")
        log_header.setStyleSheet(AppStyles.SECTION_TITLE)

        now = datetime.now()
        self.activity_container = QWidget()
        self.activity_container.setStyleSheet("background: transparent; border: none;")
        self.activity_layout = QVBoxLayout(self.activity_container)
        self.activity_layout.setContentsMargins(0, 0, 0, 0)
        self.activity_layout.setSpacing(AppStyles.INNER_PADDING - 4)

        for task in self._monthly_tasks(now):
            self._add_activity_row(task, now)

        self.activity_layout.addStretch()

        activity_scroll = QScrollArea()
        activity_scroll.setWidgetResizable(True)
        activity_scroll.setFrameShape(QFrame.NoFrame)
        activity_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        activity_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        activity_scroll.setWidget(self.activity_container)
        activity_scroll.setStyleSheet(self._scrollable_style())
        activity_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        activity_scroll.setMinimumHeight(self._activity_scroll_height_min)

        notes_card = TrueGlassPanel(border_radius=20)
        notes_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        notes_layout = QVBoxLayout(notes_card)
        notes_layout.setContentsMargins(
            AppStyles.SECTION_PADDING,
            AppStyles.SECTION_PADDING,
            AppStyles.SECTION_PADDING,
            AppStyles.SECTION_PADDING,
        )
        notes_layout.setSpacing(AppStyles.INNER_PADDING - 2)

        notes_header_row = QHBoxLayout()
        notes_header_row.setContentsMargins(0, 0, 0, 0)
        notes_header_row.setSpacing(AppStyles.INNER_PADDING - 6)

        notes_header = QLabel("Notes")
        notes_header.setStyleSheet(AppStyles.SECTION_TITLE)
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
        notes_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        notes_scroll.setWidget(self.notes_container)
        notes_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        notes_scroll.setStyleSheet(self._scrollable_style())
        notes_scroll.setMinimumHeight(self._notes_scroll_height_min)

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
        notes_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # keep references for runtime resizing logic
        self.log_card = log_card
        self.notes_card = notes_card
        self.activity_scroll = activity_scroll
        self.notes_scroll = notes_scroll
        self._activity_scroll_min_height = 190
        self._notes_scroll_min_height = 160
        self._notes_container_min_height = self.NOTES_VIEWPORT_HEIGHT

        right_panel_layout.addWidget(self.calendar_view, stretch=0)
        right_panel_layout.addSpacing(AppStyles.INNER_PADDING - 6)
        right_panel_layout.addWidget(log_card, stretch=1)
        right_panel_layout.addWidget(notes_card, stretch=0)
        self._apply_responsive_heights()
        self._load_notes_items()

        # keep right panel visible by default; do not auto-hide

    # Right panel is always visible; collapse feature removed.

    def _on_resize_debounced(self):
        # position notices after resize settles
        if hasattr(self, "delete_notices") and self.delete_notices:
            self._position_delete_notices()
        if hasattr(self, "status_notices") and self.status_notices:
            self._position_status_notices()
        # nothing else heavy here; layout children are handled in __init__

    def set_account(self, username):
        self.username = resolve_account_username(username)
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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # debounce heavy repositioning
        try:
            self._resize_timer.start(80)
        except Exception:
            pass

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
        month_key = now.strftime("%Y-%m")
        checked = self.state.get("checks", {}).get(month_key, {}).get(name, False)

        row = ActivityRowWidget(name, due_date, days_left, checked)
        row.clicked.connect(
            lambda name=name, due_date=due_date, days_left=days_left: self._show_activity_detail(name, due_date, days_left)
        )
        row.checked_changed.connect(
            lambda name, due_date, days_left, checked_state, month_key=month_key: self._save_check(month_key, name, checked_state)
        )

        self.activity_layout.addWidget(row)

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
            "created_at": str(note.get("created_at") or datetime.now().strftime("%b %d, %Y")),
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
        margin = AppStyles.NOTIFICATION_MARGIN
        gap = AppStyles.NOTIFICATION_GAP
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
        margin = AppStyles.NOTIFICATION_MARGIN
        gap = AppStyles.NOTIFICATION_GAP
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
        self._apply_responsive_heights()
        if hasattr(self, "delete_notices") and self.delete_notices:
            self._position_delete_notices()
        if hasattr(self, "status_notices") and self.status_notices:
            self._position_status_notices()

    def _apply_responsive_heights(self):
        available_height = max(
            0,
            self.height() - (AppStyles.SECTION_PADDING * 2) - (AppStyles.PANEL_SPACING_COMPACT * 2),
        )
        calendar_height = int(available_height * 0.34) if available_height else self._calendar_height_min
        calendar_height = max(self._calendar_height_min, min(self._calendar_height_max, calendar_height))

        activity_height = int(available_height * 0.28) if available_height else self._activity_scroll_height_min
        activity_height = max(self._activity_scroll_height_min, min(190, activity_height))

        notes_height = int(available_height * 0.20) if available_height else self._notes_scroll_height_min
        notes_height = max(self._notes_scroll_height_min, min(150, notes_height))

        self.calendar_view.setMinimumWidth(self._calendar_width_min)
        self.calendar_view.setMinimumHeight(calendar_height)
        self.calendar_view.setMaximumHeight(calendar_height)
        self.activity_scroll.setMinimumHeight(activity_height)
        self.notes_scroll.setMinimumHeight(notes_height)

    def _load_state(self):
        path = account_state_path(self.username, "right_panel.json")
        return load_json_dict(path, default={"notes": [], "checks": {}})

    def _save_state(self):
        path = account_state_path(self.username, "right_panel.json")
        save_json_dict(path, self.state)

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
        return AppStyles.SCROLLBAR
