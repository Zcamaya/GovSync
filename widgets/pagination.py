from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QToolButton,
    QWidget,
)
from PySide6.QtCore import Signal, Qt
from shared.constants.styles import AppStyles


class Pagination(QFrame):
    page_changed = Signal(int)

    def __init__(self, total_pages=1, current_page=1, parent=None, compact=False):
        super().__init__(parent)
        self.setObjectName("PaginationContainer")
        self._total = max(1, int(total_pages))
        self._current = max(1, int(current_page))
        self._buttons = {}
        self._compact = bool(compact)
        self._build_ui()

    def _build_ui(self):
        # base CSS uses GovSync colors
        base_css = f"""
        QFrame#PaginationContainer {{
            background: rgba(15, 23, 42, 0.72);
            border-radius: 20px;
            padding: 6px;
        }}
        QToolButton#PagArrow {{
            background: transparent;
            color: #94a3b8;
            font: 18px 'Segoe UI';
            border: none;
        }}
        QToolButton#PagNum {{
            background: transparent;
            color: #94a3b8;
            font: 700 12px 'Segoe UI';
            border: none;
            min-width: 32px;
            min-height: 32px;
            border-radius: 16px;
        }}
        QToolButton#PagNum[active="true"] {{
            background: {AppStyles.TABLE_ACCENT};
            color: #062017;
            border: 1px solid rgba(255,255,255,0.06);
            min-width: 32px;
            min-height: 32px;
            border-radius: 16px;
        }}
        """

        self.setStyleSheet(base_css)

        # inner container holds arrows and page numbers
        inner = QWidget(self)
        inner_layout = QHBoxLayout(inner)
        inner_layout.setContentsMargins(8, 6, 8, 6)
        inner_layout.setSpacing(10)

        # Prev arrow
        self.prev_btn = QToolButton(inner)
        self.prev_btn.setText("‹")
        self.prev_btn.setObjectName("PagArrow")
        self.prev_btn.setFixedSize(32, 32)
        self.prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_btn.clicked.connect(self._on_prev)
        inner_layout.addWidget(self.prev_btn)

        # pages container
        self._pages_container = QWidget(inner)
        pages_layout = QHBoxLayout(self._pages_container)
        pages_layout.setContentsMargins(0, 0, 0, 0)
        pages_layout.setSpacing(8)
        self._pages_layout = pages_layout
        inner_layout.addWidget(self._pages_container)

        # Next arrow
        self.next_btn = QToolButton(inner)
        self.next_btn.setText("›")
        self.next_btn.setObjectName("PagArrow")
        self.next_btn.setFixedSize(32, 32)
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.clicked.connect(self._on_next)
        inner_layout.addWidget(self.next_btn)

        # outer layout centers the inner widget
        outer_layout = QHBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addStretch()
        outer_layout.addWidget(inner)
        outer_layout.addStretch()

        self._rebuild_pages()
        self._update_enabled_state()

    def _rebuild_pages(self):
        # clear existing
        for i in reversed(range(self._pages_layout.count())):
            w = self._pages_layout.itemAt(i).widget()
            if w:
                w.setParent(None)
        self._buttons.clear()

        total = self._total
        current = self._current

        def add_page(p):
            btn = QToolButton(self._pages_container)
            btn.setText(str(p))
            btn.setObjectName("PagNum")
            btn.setProperty("active", "true" if p == current else "false")
            size = 24 if self._compact else 32
            btn.setFixedSize(size, size)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, page=p: self.set_page(page))
            self._pages_layout.addWidget(btn)
            self._buttons[p] = btn

        if total <= 9:
            for p in range(1, total + 1):
                add_page(p)
        else:
            add_page(1)
            if current > 4:
                ell = QToolButton(self._pages_container)
                ell.setText("...")
                ell.setObjectName("PagNum")
                ell.setEnabled(False)
                size = 24 if self._compact else 32
                ell.setFixedSize(size, size)
                self._pages_layout.addWidget(ell)
            start = max(2, current - 2)
            end = min(total - 1, current + 2)
            for p in range(start, end + 1):
                add_page(p)
            if current < total - 3:
                ell2 = QToolButton(self._pages_container)
                ell2.setText("...")
                ell2.setObjectName("PagNum")
                ell2.setEnabled(False)
                size = 24 if self._compact else 32
                ell2.setFixedSize(size, size)
                self._pages_layout.addWidget(ell2)
            add_page(total)

        # reapply active state styling
        for p, btn in self._buttons.items():
            btn.setProperty("active", "true" if p == current else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _update_enabled_state(self):
        self.prev_btn.setEnabled(self._current > 1)
        self.next_btn.setEnabled(self._current < self._total)

    def _on_prev(self):
        if self._current > 1:
            self.set_page(self._current - 1)

    def _on_next(self):
        if self._current < self._total:
            self.set_page(self._current + 1)

    def set_page(self, page: int):
        page = max(1, min(self._total, int(page)))
        if page == self._current:
            return
        self._current = page
        self._rebuild_pages()
        self._update_enabled_state()
        self.page_changed.emit(self._current)

    def update_total(self, total_pages: int):
        self._total = max(1, int(total_pages))
        if self._current > self._total:
            self._current = self._total
        self._rebuild_pages()
        self._update_enabled_state()

    def current_page(self):
        return self._current

    def set_compact(self, enabled: bool):
        # compact is handled by sizing; provide an API for callers
        if self._compact == enabled:
            return
        self._compact = enabled
        layout = self.layout() if self.layout() is not None else None
        if enabled:
            # reduce paddings and button sizes
            if layout:
                layout.setContentsMargins(4, 2, 4, 2)
                layout.setSpacing(6)
            # arrows smaller
            if hasattr(self, 'prev_btn'):
                self.prev_btn.setFixedSize(28, 28)
            if hasattr(self, 'next_btn'):
                self.next_btn.setFixedSize(28, 28)
            for btn in self._buttons.values():
                btn.setFixedSize(24, 24)
        else:
            if layout:
                layout.setContentsMargins(8, 6, 8, 6)
                layout.setSpacing(10)
            if hasattr(self, 'prev_btn'):
                self.prev_btn.setFixedSize(32, 32)
            if hasattr(self, 'next_btn'):
                self.next_btn.setFixedSize(32, 32)
            for btn in self._buttons.values():
                btn.setFixedSize(32, 32)
        self._rebuild_pages()
        self._update_enabled_state()
