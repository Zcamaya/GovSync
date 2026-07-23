from __future__ import annotations

from weakref import WeakKeyDictionary

from PySide6.QtCore import QEvent, QObject, QTimer, Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QApplication, QLabel, QAbstractScrollArea, QWidget


class LayoutDebugOverlay(QLabel):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("LayoutDebugOverlay")
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWordWrap(True)
        self.setTextFormat(Qt.PlainText)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setStyleSheet(
            """
            QLabel#LayoutDebugOverlay {
                background: rgba(2, 6, 23, 0.84);
                border: 1px solid rgba(255, 255, 255, 0.16);
                border-radius: 6px;
                color: rgba(248, 250, 252, 0.96);
                font: 600 8px 'Segoe UI';
                padding: 4px 6px;
            }
            """
        )


class LayoutDebugManager(QObject):
    """Lightweight layout debug helper.

    The debug mode uses one global stylesheet for borders and a small set of
    overlays for key containers. It avoids recursive per-resize widget styling,
    which keeps window movement and splitter dragging responsive.
    """

    _TARGET_OBJECT_NAMES = {
        "MainContainer",
        "AppPage",
        "WorkspaceStack",
        "SidebarWidget",
        "WorkspaceWidget",
        "RightPanelWidget",
        "CustomReferenceCalendar",
        "SafeSplitter",
        "TableCardWrapper",
        "TableCard",
        "AuthShell",
        "AuthCard",
        "AuthArtPanel",
        "BrandPanel",
        "FormPanel",
        "InfoPanel",
        "ContentPanel",
        "GovCard",
        "DialogCard",
        "ButtonBar",
        "HistoryCard",
        "HistoryDetailCard",
        "NoteRow",
        "ActivityRow",
        "MetricCard",
        "TrueGlassPanel",
        "RecordsTabs",
        "RecordsTab",
        "RecordsViewer",
        "RecordsContainer",
    }

    _LABEL_CLASS_NAMES = {
        "QTableWidget",
        "QTableView",
        "QListWidget",
        "QListView",
        "QTreeWidget",
        "QTreeView",
        "QAbstractItemView",
        "SharedTable",
        "RoundedTableCard",
        "EmployeeRecordsTable",
        "DraggableTableWidget",
        "QLabel",
        "QPushButton",
        "QToolButton",
        "QCheckBox",
        "QRadioButton",
        "QTabWidget",
        "QTabBar",
        "QDialog",
        "QDialogButtonBox",
        "QGroupBox",
        "QFrame",
        "QAbstractButton",
        "QCommandLinkButton",
        "QLineEdit",
        "QTextEdit",
        "QPlainTextEdit",
        "QComboBox",
        "QAbstractSpinBox",
        "QDateEdit",
        "QDateTimeEdit",
        "QTimeEdit",
        "QMenuBar",
        "QMenu",
        "QStatusBar",
        "QListWidget",
        "GlassDialog",
        "LoginDialog",
        "RegisterDialog",
        "SuperAdminWindow",
        "SingleTablePopup",
        "HistoryCardWidget",
        "EmployeeRecordsPanel",
        "EmployerAdminPanel",
        "EarningsPanel",
        "HDMFLoanPanel",
        "SSSPanel",
        "PhilHealthPanel",
        "TrueGlassPanel",
    }

    _INHERIT_TARGETS = (
        "QAbstractButton",
        "QAbstractItemView",
        "QAbstractScrollArea",
        "QAbstractSpinBox",
        "QComboBox",
        "QDateEdit",
        "QDateTimeEdit",
        "QDialog",
        "QLineEdit",
        "QPlainTextEdit",
        "QRadioButton",
        "QTabBar",
        "QTabWidget",
        "QTextEdit",
        "QTimeEdit",
    )

    _BORDER_COLORS = [
        "rgba(239, 68, 68, 0.72)",
        "rgba(34, 197, 94, 0.72)",
        "rgba(59, 130, 246, 0.72)",
        "rgba(249, 115, 22, 0.72)",
        "rgba(168, 85, 247, 0.72)",
    ]

    def __init__(self, app: QApplication, enabled: bool = False):
        super().__init__(app)
        self.app = app
        self.enabled = enabled
        self.borders_enabled = enabled
        self.labels_enabled = False
        self._base_app_stylesheet = app.styleSheet()
        self._refresh_pending = False
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.timeout.connect(self._apply_now)
        self._shortcuts: list[QShortcut] = []
        self._overlay_targets = WeakKeyDictionary()
        self._overlays = WeakKeyDictionary()
        self._original_stylesheets = WeakKeyDictionary()
        self._watched_windows = WeakKeyDictionary()
        app.installEventFilter(self)

    def attach_window(self, window: QWidget):
        self._install_shortcuts(window)
        self._watch_window(window)
        self._collect_overlay_targets(window)
        if self.enabled:
            self._apply_app_stylesheet()
            self._apply_target_styles()
            self.refresh()

    def enable(self):
        self.enabled = True
        self.borders_enabled = True
        self._apply_app_stylesheet()
        self._apply_target_styles()
        self.refresh()

    def disable(self):
        self.enabled = False
        self.borders_enabled = False
        self.labels_enabled = False
        self._remove_all_overlays()
        self._restore_all_target_styles()
        self._restore_all_stylesheets()
        self.app.setStyleSheet(self._base_app_stylesheet)

    def toggle(self):
        if self.enabled:
            self.disable()
        else:
            self.enable()

    def toggle_borders(self):
        self.borders_enabled = not self.borders_enabled
        self.enabled = self.borders_enabled or self.labels_enabled
        if not self.enabled:
            self.disable()
            return
        self._apply_app_stylesheet()
        self._apply_target_styles()
        self.refresh()

    def toggle_labels(self):
        self.labels_enabled = not self.labels_enabled
        self.enabled = self.borders_enabled or self.labels_enabled
        if not self.enabled:
            self.disable()
            return
        self.refresh()

    def eventFilter(self, obj, event):
        if not self.enabled:
            return super().eventFilter(obj, event)

        if isinstance(obj, QWidget):
            if (
                event.type() == QEvent.Show
                and obj.isWindow()
                and obj not in self._watched_windows
            ):
                self._watch_window(obj)
                self._collect_overlay_targets(obj)
                self._apply_target_styles()
                self.refresh()
            elif obj in self._watched_windows and event.type() in (QEvent.Show, QEvent.Resize, QEvent.WindowStateChange, QEvent.LayoutRequest):
                self.refresh()
            elif obj in self._overlay_targets and event.type() in (QEvent.Show, QEvent.Resize, QEvent.LayoutRequest):
                self.refresh()

        return super().eventFilter(obj, event)

    def refresh(self):
        if not self.enabled:
            return

        self._refresh_timer.start(180)

    def _apply_now(self):
        if not self.enabled:
            return

        if self.labels_enabled:
            for widget, depth in list(self._overlay_targets.items()):
                if widget is None or not widget.isVisible():
                    continue
                self._ensure_overlay(widget, depth)
        else:
            self._remove_all_overlays()

    def _watch_window(self, window: QWidget):
        self._watched_windows[window] = True

    def _collect_overlay_targets(self, root: QWidget):
        for widget in root.findChildren(QWidget):
            class_name = widget.metaObject().className()
            object_name = widget.objectName()
            if (
                object_name in self._TARGET_OBJECT_NAMES
                or class_name in self._LABEL_CLASS_NAMES
                or any(widget.inherits(name) for name in self._INHERIT_TARGETS)
                or widget.isWindow()
            ):
                self._overlay_targets[widget] = self._estimate_depth(widget)

    def _estimate_depth(self, widget: QWidget) -> int:
        depth = 1
        parent = widget.parentWidget()
        while parent is not None:
            depth += 1
            parent = parent.parentWidget()
        return depth

    def _ensure_overlay(self, widget: QWidget, depth: int):
        if widget not in self._overlays:
            overlay = LayoutDebugOverlay(widget)
            self._overlays[widget] = overlay

        overlay = self._overlays.get(widget)
        if overlay is None:
            return

        overlay.setText(self._build_overlay_text(widget, depth))
        overlay.adjustSize()
        self._position_overlay(widget, overlay)
        overlay.show()
        overlay.raise_()

    def _position_overlay(self, widget: QWidget, overlay: QLabel):
        margin = widget.contentsMargins()
        x = max(6, margin.left() + 4)
        y = max(6, margin.top() + 4)
        width = min(240, max(120, widget.width() - x - 8))
        overlay.setFixedWidth(width)
        overlay.move(x, y)

    def _build_overlay_text(self, widget: QWidget, depth: int) -> str:
        layout = widget.layout()
        object_name = widget.objectName() or "-"
        parts = [
            f"{widget.metaObject().className()} #{object_name}",
            f"size {widget.width()}x{widget.height()}",
            f"min {widget.minimumWidth()}x{widget.minimumHeight()}",
            f"max {widget.maximumWidth()}x{widget.maximumHeight()}",
        ]
        if layout is not None:
            margins = layout.contentsMargins()
            parts.append(
                f"layout {layout.__class__.__name__} m={margins.left()}/{margins.top()}/{margins.right()}/{margins.bottom()} s={layout.spacing()} a={int(layout.alignment())}"
            )
        parts.append(f"depth {depth}")
        return "\n".join(parts)

    def _remove_all_overlays(self):
        for widget in list(self._overlays.keys()):
            overlay = self._overlays.pop(widget, None)
            if overlay is not None:
                overlay.hide()
                overlay.deleteLater()

    def _restore_all_stylesheets(self):
        for widget, original in list(self._original_stylesheets.items()):
            if widget is None:
                continue
            widget.setStyleSheet(original)
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()
        self._original_stylesheets.clear()

    def _apply_target_styles(self):
        if not self.borders_enabled:
            return

        for widget, depth in list(self._overlay_targets.items()):
            if widget is None:
                continue
            self._style_widget(widget, depth=depth)
            if isinstance(widget, QAbstractScrollArea):
                viewport = widget.viewport()
                if viewport is not None:
                    self._style_widget(viewport, depth=depth + 1, viewport=True)

    def _restore_all_target_styles(self):
        for widget, original in list(self._original_stylesheets.items()):
            if widget is None:
                continue
            widget.setStyleSheet(original)
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()
        self._original_stylesheets.clear()

    def _style_widget(self, widget: QWidget, depth: int, viewport: bool = False):
        original = self._original_stylesheets.get(widget)
        if original is None:
            original = widget.styleSheet()
            self._original_stylesheets[widget] = original

        object_name = widget.objectName().strip()
        selector = f"#{object_name}" if object_name else widget.metaObject().className()
        color = self._BORDER_COLORS[(max(depth, 1) - 1) % len(self._BORDER_COLORS)]

        if viewport:
            debug_border = f"""
                border: 1px dashed {color};
            """
        else:
            debug_border = f"""
                border: 1px solid {color};
                border-radius: 12px;
            """

        widget.setStyleSheet(
            original
            + f"""
            /* layout debug */
            {selector} {{
                {debug_border}
            }}
            """
        )

    def _install_shortcuts(self, window: QWidget):
        shortcuts = [
            ("Ctrl+Shift+D", self.toggle),
            ("Ctrl+Shift+G", self.toggle_borders),
            ("Ctrl+Shift+M", self.toggle_labels),
        ]

        for sequence, callback in shortcuts:
            shortcut = QShortcut(QKeySequence(sequence), window)
            shortcut.setContext(Qt.ApplicationShortcut)
            shortcut.activated.connect(callback)
            self._shortcuts.append(shortcut)

    def _apply_app_stylesheet(self):
        if not self.borders_enabled:
            self.app.setStyleSheet(self._base_app_stylesheet)
            return

        debug_styles = """
            QSplitter {
                background: transparent;
            }
            QSplitter::handle {
                background: rgba(148, 163, 184, 0.12);
                border: 1px solid rgba(148, 163, 184, 0.22);
            }
            QSplitter::handle:hover {
                background: rgba(59, 130, 246, 0.22);
                border-color: rgba(59, 130, 246, 0.42);
            }

            QPushButton,
            QToolButton,
            QCheckBox,
            QRadioButton,
            QCommandLinkButton,
            QTabBar::tab,
            QDialogButtonBox QPushButton,
            QGroupBox,
            QLabel {
                border: 1px solid rgba(59, 130, 246, 0.24);
            }
            QAbstractButton,
            QToolButton,
            QPushButton,
            QCheckBox,
            QRadioButton,
            QCommandLinkButton {
                border-radius: 10px;
            }
            QLabel {
                border: 1px dotted rgba(168, 85, 247, 0.16);
            }

            QTabWidget {
                border: 1px solid rgba(168, 85, 247, 0.20);
            }
            QTabWidget::pane {
                border: 1px solid rgba(168, 85, 247, 0.16);
            }
            QTabBar {
                background: transparent;
            }
            QTabBar::tab {
                margin: 1px;
                padding: 4px 8px;
            }
            QTabBar::tab:selected {
                border-color: rgba(59, 130, 246, 0.36);
            }

            QAbstractScrollArea,
            QScrollArea {
                border: 1px solid rgba(34, 197, 94, 0.20);
                border-radius: 12px;
            }
            QAbstractScrollArea::viewport,
            QScrollArea::viewport {
                border: 1px dashed rgba(34, 197, 94, 0.20);
                border-radius: 11px;
            }
            QAbstractItemView,
            QTableWidget::item,
            QTableView::item,
            QTreeView::item,
            QTreeWidget::item,
            QListView::item {
                border: 1px solid rgba(34, 197, 94, 0.12);
            }

            QTableWidget,
            QTableView {
                border: 1px solid rgba(244, 63, 94, 0.18);
                border-radius: 12px;
            }
            QTableWidget::viewport,
            QTableView::viewport {
                border: 1px dashed rgba(244, 63, 94, 0.18);
                border-radius: 11px;
            }
            QTableWidget::item:selected,
            QTableView::item:selected,
            QTreeView::item:selected,
            QTreeWidget::item:selected,
            QListView::item:selected {
                border: 1px solid rgba(59, 130, 246, 0.22);
            }
            QListWidget,
            QListView,
            QTreeWidget,
            QTreeView {
                border: 1px solid rgba(244, 63, 94, 0.16);
                border-radius: 10px;
            }
            QListWidget::item,
            QListView::item,
            QTreeWidget::item,
            QTreeView::item {
                border: 1px solid rgba(34, 197, 94, 0.12);
                border-radius: 8px;
            }
            QListWidget::item:selected {
                border: 1px solid rgba(59, 130, 246, 0.22);
                border-radius: 8px;
            }
            QHeaderView::section {
                border: 1px solid rgba(249, 115, 22, 0.18);
            }
            QTableCornerButton::section {
                border: 1px solid rgba(249, 115, 22, 0.18);
            }

            QLineEdit,
            QTextEdit,
            QPlainTextEdit,
            QComboBox,
            QAbstractSpinBox {
                border: 1px solid rgba(56, 189, 248, 0.22);
                border-radius: 10px;
            }
            QComboBox::drop-down {
                border-left: 1px solid rgba(56, 189, 248, 0.18);
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
            }

            QMenuBar,
            QMenu,
            QStatusBar {
                border: 1px solid rgba(168, 85, 247, 0.16);
            }

            QScrollBar:vertical,
            QScrollBar:horizontal {
                border: 1px solid rgba(148, 163, 184, 0.24);
                background: rgba(2, 6, 23, 0.16);
            }
            QScrollBar::handle:vertical,
            QScrollBar::handle:horizontal {
                background: rgba(148, 163, 184, 0.30);
            }
        """
        self.app.setStyleSheet(self._base_app_stylesheet + debug_styles)
