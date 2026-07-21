from PySide6.QtCore import QEvent, Qt, QPropertyAnimation, QEasingCurve, QTimer, QRectF
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHeaderView,
    QSizePolicy,
    QScrollBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtGui import QPainterPath, QRegion

from constants.styles import AppStyles


class OverlayScrollBar(QScrollBar):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setCursor(Qt.ArrowCursor)
        self.setStyleSheet(
            """
            QScrollBar {
                background: transparent;
                width: 8px;
                height: 8px;
                margin: 0px;
            }
            QScrollBar::handle {
                background: rgba(148, 163, 184, 0.24);
                border-radius: 4px;
                min-height: 28px;
                min-width: 28px;
            }
            QScrollBar::handle:hover {
                background: rgba(148, 163, 184, 0.42);
            }
            QScrollBar::add-line, QScrollBar::sub-line,
            QScrollBar::add-page, QScrollBar::sub-page {
                background: transparent;
                border: none;
                height: 0;
                width: 0;
            }
            """
        )
        effect = QGraphicsOpacityEffect(self)
        effect.setOpacity(0.0)
        self.setGraphicsEffect(effect)
        self._fade = QPropertyAnimation(effect, b"opacity", self)
        self._fade.setDuration(220)
        self._fade.setEasingCurve(QEasingCurve.InOutQuad)
        self._fade.finished.connect(self._on_fade_out_finished)
        self.hide()

    def fade_in(self):
        self._fade.stop()
        self.show()
        self._fade.setStartValue(self.graphicsEffect().opacity())
        self._fade.setEndValue(1.0)
        self._fade.start()

    def fade_out(self):
        self._fade.stop()
        self._fade.setStartValue(self.graphicsEffect().opacity())
        self._fade.setEndValue(0.0)
        self._fade.start()

    def _on_fade_out_finished(self):
        if self.graphicsEffect().opacity() <= 0.01:
            self.hide()


class SharedTable(QTableWidget):
    def __init__(self, columns=None, parent=None):
        super().__init__(0, len(columns or []), parent)
        self._build_ui(columns or [])

    def _build_ui(self, columns):
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFrameShape(QFrame.NoFrame)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setShowGrid(False)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSortingEnabled(False)
        self.verticalHeader().setVisible(False)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWordWrap(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(260)
        self.setStyleSheet(AppStyles.TABLE_CANONICAL)
        self.set_row_height(AppStyles.TABLE_ROW_HEIGHT)
        if columns:
            self.setHorizontalHeaderLabels(columns)
        header = self.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header.setStretchLastSection(False)
        header.setHighlightSections(False)
        header.setMinimumHeight(AppStyles.TABLE_HEADER_HEIGHT)

        self._overlay_vscrollbar = OverlayScrollBar(Qt.Vertical, self)
        self._overlay_hscrollbar = OverlayScrollBar(Qt.Horizontal, self)
        self._overlay_vscrollbar.setVisible(False)
        self._overlay_hscrollbar.setVisible(False)
        self._overlay_vscrollbar.setMouseTracking(True)
        self._overlay_hscrollbar.setMouseTracking(True)
        self.setMouseTracking(True)
        self._hide_scrollbars_timer = QTimer(self)
        self._hide_scrollbars_timer.setSingleShot(True)
        self._hide_scrollbars_timer.timeout.connect(self._hide_scrollbars)

        self.verticalScrollBar().valueChanged.connect(self._sync_vertical_scrollbar)
        self.horizontalScrollBar().valueChanged.connect(self._sync_horizontal_scrollbar)
        self.verticalScrollBar().rangeChanged.connect(self._sync_vertical_range)
        self.horizontalScrollBar().rangeChanged.connect(self._sync_horizontal_range)
        self._overlay_vscrollbar.valueChanged.connect(self.verticalScrollBar().setValue)
        self._overlay_hscrollbar.valueChanged.connect(self.horizontalScrollBar().setValue)
        self.installEventFilter(self)
        self.viewport().installEventFilter(self)
        self.viewport().setAttribute(Qt.WA_StyledBackground, True)
        self._sync_vertical_range(0, self.verticalScrollBar().maximum())
        self._sync_horizontal_range(0, self.horizontalScrollBar().maximum())

    def eventFilter(self, obj, event):
        if obj in (self, self.viewport()):
            if event.type() == QEvent.Enter:
                self._show_scrollbars()
                self._hide_scrollbars_timer.stop()
            elif event.type() == QEvent.Leave:
                self._start_hide_timer()
        return super().eventFilter(obj, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_round_mask(self, 14)
        self._apply_round_mask(self.viewport(), 14)
        # Debounce overlay scrollbar position updates
        try:
            if not hasattr(self, "_resize_debounce_timer"):
                from PySide6.QtCore import QTimer

                self._resize_debounce_timer = QTimer(self)
                self._resize_debounce_timer.setSingleShot(True)
                self._resize_debounce_timer.timeout.connect(self._update_scrollbar_positions)
            self._resize_debounce_timer.start(40)
        except Exception:
            self._update_scrollbar_positions()

    def _apply_round_mask(self, widget, radius: int):
        rect = widget.rect()
        if rect.width() <= 0 or rect.height() <= 0:
            return
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), radius, radius)
        widget.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def wheelEvent(self, event):
        self._show_scrollbars()
        self._start_hide_timer()
        super().wheelEvent(event)

    def _update_scrollbar_positions(self):
        viewport_geom = self.viewport().geometry()
        margin = 6
        v_width = 8
        h_height = 8
        self._overlay_vscrollbar.setGeometry(
            viewport_geom.right() - v_width - margin,
            viewport_geom.top() + margin,
            v_width,
            max(0, viewport_geom.height() - h_height - 2 * margin),
        )
        self._overlay_hscrollbar.setGeometry(
            viewport_geom.left() + margin,
            viewport_geom.bottom() - h_height - margin,
            max(0, viewport_geom.width() - v_width - 2 * margin),
            h_height,
        )
        self._overlay_vscrollbar.raise_()
        self._overlay_hscrollbar.raise_()

    def _sync_vertical_scrollbar(self, value):
        if self._overlay_vscrollbar.value() != value:
            self._overlay_vscrollbar.setValue(value)
        self._show_scrollbars()
        self._start_hide_timer()

    def _sync_horizontal_scrollbar(self, value):
        if self._overlay_hscrollbar.value() != value:
            self._overlay_hscrollbar.setValue(value)
        self._show_scrollbars()
        self._start_hide_timer()

    def _sync_vertical_range(self, minimum, maximum):
        self._overlay_vscrollbar.setRange(minimum, maximum)
        self._overlay_vscrollbar.setPageStep(self.verticalScrollBar().pageStep())
        self._overlay_vscrollbar.setSingleStep(self.verticalScrollBar().singleStep())
        self._overlay_vscrollbar.setVisible(maximum > 0)
        self._update_scrollbar_positions()

    def _sync_horizontal_range(self, minimum, maximum):
        self._overlay_hscrollbar.setRange(minimum, maximum)
        self._overlay_hscrollbar.setPageStep(self.horizontalScrollBar().pageStep())
        self._overlay_hscrollbar.setSingleStep(self.horizontalScrollBar().singleStep())
        self._overlay_hscrollbar.setVisible(maximum > 0)
        self._update_scrollbar_positions()

    def _show_scrollbars(self):
        if self.verticalScrollBar().maximum() > 0:
            self._overlay_vscrollbar.fade_in()
        if self.horizontalScrollBar().maximum() > 0:
            self._overlay_hscrollbar.fade_in()

    def _hide_scrollbars(self):
        self._overlay_vscrollbar.fade_out()
        self._overlay_hscrollbar.fade_out()

    def _start_hide_timer(self):
        self._hide_scrollbars_timer.start(900)

    def set_columns(self, columns):
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)

    def set_stretch_columns(self, *indices):
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for index in indices:
            self.horizontalHeader().setSectionResizeMode(index, QHeaderView.Stretch)

    def set_resize_to_contents(self, *indices):
        for index in indices:
            self.horizontalHeader().setSectionResizeMode(index, QHeaderView.ResizeToContents)

    def set_row_height(self, height):
        self.verticalHeader().setDefaultSectionSize(height)

    def set_empty_state(self, message="No records found"):
        self.setRowCount(1)
        self.clearContents()
        empty_item = QTableWidgetItem(message)
        empty_item.setFlags(empty_item.flags() & ~Qt.ItemIsEditable)
        empty_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.setItem(0, 0, empty_item)
        self.setSpan(0, 0, 1, max(1, self.columnCount()))
        self.setRowHeight(0, max(72, AppStyles.TABLE_ROW_HEIGHT + 24))

    def clear_rows(self):
        self.setRowCount(0)
        self.clearContents()


class RoundedTableCard(QWidget):
    def __init__(self, columns=None, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setObjectName("TableCardWrapper")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self.card = QFrame(self)
        self.card.setObjectName("TableCard")
        self.card.setAttribute(Qt.WA_StyledBackground, True)
        self.card.setStyleSheet(AppStyles.TABLE_CARD)

        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(
            AppStyles.TABLE_CARD_PADDING,
            AppStyles.TABLE_CARD_PADDING,
            AppStyles.TABLE_CARD_PADDING,
            AppStyles.TABLE_CARD_PADDING,
        )
        self.card_layout.setSpacing(0)

        self.table = SharedTable(columns or [], self.card)
        self.table.setAttribute(Qt.WA_StyledBackground, True)
        self.table.setStyleSheet(AppStyles.TABLE_CANONICAL)
        self.table.viewport().setAttribute(Qt.WA_StyledBackground, True)
        self.card_layout.addWidget(self.table)
        self._layout.addWidget(self.card)

    def setStyleSheet(self, style):
        # Treat style calls as applying to the inner table.
        self.table.setStyleSheet(style)

    def __getattr__(self, name):
        return getattr(self.table, name)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_round_mask(self, 18)
        self._apply_round_mask(self.card, 18)
        self._apply_round_mask(self.table, 14)
        self._apply_round_mask(self.table.viewport(), 14)

    def _apply_round_mask(self, widget, radius: int):
        rect = widget.rect()
        if rect.width() <= 0 or rect.height() <= 0:
            return
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), radius, radius)
        widget.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def _sync_horizontal_range(self, minimum, maximum):
        self._overlay_hscrollbar.setRange(minimum, maximum)
        self._overlay_hscrollbar.setPageStep(self.horizontalScrollBar().pageStep())
        self._overlay_hscrollbar.setSingleStep(self.horizontalScrollBar().singleStep())
        self._overlay_hscrollbar.setVisible(maximum > 0)
        self._update_scrollbar_positions()

    def _show_scrollbars(self):
        if self.verticalScrollBar().maximum() > 0:
            self._overlay_vscrollbar.fade_in()
        if self.horizontalScrollBar().maximum() > 0:
            self._overlay_hscrollbar.fade_in()

    def _hide_scrollbars(self):
        self._overlay_vscrollbar.fade_out()
        self._overlay_hscrollbar.fade_out()

    def _start_hide_timer(self):
        self._hide_scrollbars_timer.start(900)

    def set_columns(self, columns):
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)

    def set_stretch_columns(self, *indices):
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for index in indices:
            self.horizontalHeader().setSectionResizeMode(index, QHeaderView.Stretch)

    def set_resize_to_contents(self, *indices):
        for index in indices:
            self.horizontalHeader().setSectionResizeMode(index, QHeaderView.ResizeToContents)

    def set_row_height(self, height):
        self.verticalHeader().setDefaultSectionSize(height)

    def set_empty_state(self, message="No records found"):
        self.setRowCount(1)
        self.clearContents()
        empty_item = QTableWidgetItem(message)
        empty_item.setFlags(empty_item.flags() & ~Qt.ItemIsEditable)
        empty_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.setItem(0, 0, empty_item)
        self.setSpan(0, 0, 1, max(1, self.columnCount()))
        self.setRowHeight(0, max(72, AppStyles.TABLE_ROW_HEIGHT + 24))

    def clear_rows(self):
        self.setRowCount(0)
        self.clearContents()
