from PySide6.QtWidgets import QFrame, QHBoxLayout, QWidget
from PySide6.QtCore import Slot

from widgets.pagination import Pagination


class EmployeeRecordsPaginator(QFrame):
    def __init__(self, total=1, current=1, parent=None):
        # Backwards compatibility: callers sometimes pass only parent as first arg
        if parent is None and isinstance(total, QWidget):
            parent = total
            total = 1
            current = 1

        super().__init__(parent)
        self._compact_mode = False
        self._pagination = Pagination(total_pages=total, current_page=current, parent=self)
        # use compact pagination by default to match table footer design
        self._pagination.set_compact(True)
        self._build_ui()

    def _build_ui(self):
        # make the paginator more compact by default but tall enough to avoid clipping
        self.setMinimumHeight(48)
        self.setMaximumHeight(64)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addStretch()
        layout.addWidget(self._pagination)
        layout.addStretch()

    def set_compact_mode(self, enabled: bool):
        # compact mode currently adjusts height only
        if self._compact_mode == enabled:
            return
        self._compact_mode = enabled
        if enabled:
            self.setMinimumHeight(30)
            self.setMaximumHeight(40)
        else:
            self.setMinimumHeight(36)
            self.setMaximumHeight(48)

    def update_page(self, page):
        self._pagination.set_page(page)

    def update_total(self, total):
        self._pagination.update_total(total)

    def current_page(self):
        return self._pagination.current_page()

    def on_page_changed(self, callback):
        self._pagination.page_changed.connect(callback)
