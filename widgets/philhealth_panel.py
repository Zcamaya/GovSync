import os
from datetime import datetime

from PySide6.QtCore import QPoint, QTimer, Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QDialog,
    QFrame,
    QGridLayout,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox as NativeMessageBox,
    QProgressBar,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QSizePolicy,
    QWidget,
)

from constants.styles import AppStyles
from controllers.philhealth_controller import PhilHealthController
from widgets.glass_dialog import GlassDialog
from repositories.history_repository import HistoryRepository
from repositories.statistics_repository import StatisticsRepository
from services.philhealth_service import PhilHealthService
from services.auth_manager import database_path, get_account, get_active_account, set_active_account
from shared.ui import set_exit_icon


class SingleTablePopup(QDialog):
    def __init__(self, title, headers, data, parent=None, tabs=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setModal(True)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setMinimumSize(860, 560)
        self.drag_pos = QPoint()
        self.headers = list(headers)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title_row = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #f8fafc; font: 800 16px 'Segoe UI';")
        close_btn = QPushButton()
        close_btn.setFixedSize(28, 28)
        set_exit_icon(close_btn, "#93c5fd", 11)
        close_btn.setStyleSheet(AppStyles.SQUARE_CLOSE_BUTTON)
        close_btn.clicked.connect(self.reject)
        title_row.addWidget(title_label)
        title_row.addStretch()
        title_row.addWidget(close_btn)
        layout.addLayout(title_row)

        if tabs:
            tab_widget = QTabWidget()
            tab_widget.setStyleSheet(AppStyles.HISTORY_SURFACE)
            for label, rows in tabs:
                tab_widget.addTab(self._create_table(rows), label)
            layout.addWidget(tab_widget)
        else:
            layout.addWidget(self._create_table(data))

    def _create_table(self, data):
        table = DraggableTableWidget()
        table.setColumnCount(len(self.headers) + 1)
        table.setHorizontalHeaderLabels(["No."] + self.headers)
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setDragDropMode(QAbstractItemView.NoDragDrop)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._apply_table_widths(table)
        table.setAlternatingRowColors(True)
        table.setStyleSheet(AppStyles.HISTORY_SURFACE)
        self._populate_table(table, data)
        return table

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

    def _apply_table_widths(self, table):
        header = table.horizontalHeader()
        header.setStretchLastSection(False)
        widths = [70, 170, 130, 320, 120]
        for column_index, width in enumerate(widths[: table.columnCount()]):
            header.setSectionResizeMode(column_index, QHeaderView.Interactive)
            table.setColumnWidth(column_index, width)
        if table.columnCount() >= 4:
            header.setSectionResizeMode(3, QHeaderView.Stretch)

    def _populate_table(self, table, data):
        table.setRowCount(len(data))
        for row_index, row in enumerate(data, start=1):
            index_item = QTableWidgetItem(str(row_index))
            index_item.setFlags(index_item.flags() & ~Qt.ItemIsEditable)
            index_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row_index - 1, 0, index_item)
            for column_index, value in enumerate(row, start=1):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row_index - 1, column_index, item)


class DraggableTableWidget(QTableWidget):
    def dropEvent(self, event):
        super().dropEvent(event)
        for row_index in range(self.rowCount()):
            item = self.item(row_index, 0)
            if item is None:
                item = QTableWidgetItem()
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.setItem(row_index, 0, item)
            item.setText(str(row_index + 1))


class HistoryCardWidget(QFrame):
    delete_requested = Signal(str)
    opened = Signal(dict)
    OPEN_HOTSPOT_HEIGHT = 56

    def __init__(self, record, parent=None):
        super().__init__(parent)
        self.record = record
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("HistoryCard")
        self._setup_ui()

    def _setup_ui(self):
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedSize(220, 140)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setStyleSheet("""
            QFrame#HistoryCard {
                background: rgba(20, 43, 37, 0.58);
                border: 1px solid rgba(148, 163, 184, 0.20);
                border-radius: 8px;
            }
            QFrame#HistoryCard:hover {
                border-color: rgba(20, 184, 166, 0.36);
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        header = QHBoxLayout()
        header.setSpacing(6)
        title = QLabel(self.record.get("month_year", "Unknown"))
        title.setStyleSheet("color: #f8fafc; font: 800 14px 'Segoe UI';")
        header.addWidget(title)
        header.addStretch()
        delete_btn = QPushButton()
        delete_btn.setFixedSize(28, 28)
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setToolTip("Remove record")
        set_exit_icon(delete_btn, "#fb7185", 16)
        delete_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 8px;
                padding: 0;
            }
            QPushButton:hover {
                background: rgba(244, 63, 94, 0.16);
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.record.get("id", "")))
        header.addWidget(delete_btn, alignment=Qt.AlignRight | Qt.AlignVCenter)
        layout.addLayout(header)

        created = self.record.get("created_at") or self.record.get("month_year", "")
        badge = QLabel(f"Date Created: {created}")
        badge.setStyleSheet(
            "color: #bfdbfe; background: rgba(59, 130, 246, 0.16); border-radius: 10px; padding: 4px 8px; font: 700 10px 'Segoe UI';"
        )
        layout.addWidget(badge)

        metrics_layout = QVBoxLayout()
        metrics_layout.setSpacing(4)

        def make_row(label, val, color):
            row = QHBoxLayout()
            row_lbl = QLabel(label)
            row_lbl.setStyleSheet("color: #94a3b8; font: 11px 'Segoe UI';")
            row_val = QLabel(str(val))
            row_val.setStyleSheet(f"color: {color}; font: 700 12px 'Segoe UI';")
            row.addWidget(row_lbl)
            row.addStretch()
            row.addWidget(row_val)
            return row

        metrics_layout.addLayout(make_row("Total Employees:", self.record.get("total_count", 0), "#3b82f6"))
        metrics_layout.addLayout(make_row("Missing:", self.record.get("missing_count", 0), "#f59e0b"))
        metrics_layout.addLayout(make_row("Newly Hired:", self.record.get("new_count", 0), "#10b981"))
        layout.addLayout(metrics_layout)
        layout.addStretch()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.position().y() <= self.OPEN_HOTSPOT_HEIGHT:
            self.opened.emit(self.record)
        super().mousePressEvent(event)


class HistoryDetailCard(QFrame):
    closed = Signal()

    def __init__(self, record, parent=None):
        super().__init__(parent)
        self.record = record
        self.setObjectName("HistoryDetailCard")
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("""
            QLabel {
                color: #e5e7eb;
                background: transparent;
                border: none;
            }
            QTableWidget::item {
                color: #e5e7eb;
                padding: 5px 8px;
            }
        """ + AppStyles.HISTORY_SURFACE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel(f"Historical Records: {self.record.get('month_year', '')}")
        title.setStyleSheet("color: #f8fafc; font: 800 16px 'Segoe UI';")
        close_btn = QPushButton()
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(Qt.PointingHandCursor)
        set_exit_icon(close_btn, "#93c5fd", 11)
        close_btn.setStyleSheet(AppStyles.SQUARE_CLOSE_BUTTON)
        close_btn.clicked.connect(self.closed.emit)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_btn)
        layout.addLayout(header)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(AppStyles.HISTORY_SURFACE)
        self.tabs.setDocumentMode(True)
        self.tabs.addTab(self._create_table(self.record.get("data_total", [])), "Active")
        self.tabs.addTab(self._create_table(self.record.get("data_missing", [])), "Missing")
        self.tabs.addTab(self._create_table(self.record.get("data_new", [])), "Newly Hired")
        layout.addWidget(self.tabs)

    def _apply_table_widths(self, table):
        header = table.horizontalHeader()
        header.setStretchLastSection(False)
        widths = [68, 170, 130, 320, 120]
        for column_index, width in enumerate(widths):
            header.setSectionResizeMode(column_index, QHeaderView.Interactive)
            table.setColumnWidth(column_index, width)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

    def _create_table(self, data):
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "No.",
            "Client",
            "PhilHealth No",
            "Employee Name",
            "Birthdate",
        ])
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setDragDropMode(QAbstractItemView.NoDragDrop)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setMinimumHeight(320)
        table.setMinimumWidth(760)
        self._apply_table_widths(table)
        self._populate_table(table, data)
        return table

    def _populate_table(self, table, data):
        table.setRowCount(len(data))
        for row_index, row in enumerate(data, start=1):
            index_item = QTableWidgetItem(str(row_index))
            index_item.setFlags(index_item.flags() & ~Qt.ItemIsEditable)
            index_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row_index - 1, 0, index_item)

            for column_index, value in enumerate(row[:4], start=1):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if column_index in (2, 4):
                    item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row_index - 1, column_index, item)


class GovSyncMessageBox:
    Yes = NativeMessageBox.Yes
    No = NativeMessageBox.No

    @staticmethod
    def _can_show_dialog():
        return QApplication.instance() is not None

    @staticmethod
    def information(parent, title, message):
        if not GovSyncMessageBox._can_show_dialog():
            return NativeMessageBox.Ok
        GlassDialog(parent, title, message).exec()
        return NativeMessageBox.Ok

    @staticmethod
    def warning(parent, title, message):
        if not GovSyncMessageBox._can_show_dialog():
            return NativeMessageBox.Ok
        GlassDialog(parent, title, message).exec()
        return NativeMessageBox.Ok

    @staticmethod
    def error(parent, title, message):
        if not GovSyncMessageBox._can_show_dialog():
            return NativeMessageBox.Ok
        GlassDialog(parent, title, message).exec()
        return NativeMessageBox.Ok

    @staticmethod
    def question(parent, title, message, buttons=None):
        if not GovSyncMessageBox._can_show_dialog():
            return NativeMessageBox.Yes
        dialog = GlassDialog(
            parent,
            title,
            message,
            buttons=[
                ("No", lambda: dialog.reject(), False),
                ("Yes", lambda: dialog.accept(), True),
            ],
        )
        return NativeMessageBox.Yes if dialog.exec() == GlassDialog.Accepted else NativeMessageBox.No


class PhilHealthPanel(QWidget):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.current_username = "default"
        self.is_processing = False
        self.detail_popups = []
        self.selected_history_record_id = None
        self.controller = controller or PhilHealthController(
            PhilHealthService(
                HistoryRepository(database_path()),
                StatisticsRepository(database_path()),
                message_box_class=GovSyncMessageBox,
            )
        )
        self.engine = self.controller.get_engine()
        self.engine.setVisible(False)
        self._connect_reference_callbacks()
        self._setup_ui()
        self._restore_latest_process_state()

    def _connect_reference_callbacks(self):
        self.engine.show_history_detail_popup = self._show_history_detail_popup
        self.engine.show_current_detail_popup = self._show_current_detail_popup
        self.engine.render_history_grid = self._render_history_grid
        self.engine.delete_history_record = self._delete_history_record
        self.engine.save_history_record = self._save_history_record
        self._hide_redundant_tabs()
        self.engine.load_history()
        self.controller.engine = self.engine

    def _hide_redundant_tabs(self):
        if not hasattr(self.engine, "tab_container"):
            return
        for index in reversed(range(self.engine.tab_container.count())):
            label = self.engine.tab_container.tabText(index)
            if label in {"Missing Names", "Newly Hired"}:
                self.engine.tab_container.removeTab(index)

    def _resolve_username(self, account_or_username):
        if isinstance(account_or_username, dict):
            return str(account_or_username.get("username", "")).strip() or "default"
        return str(account_or_username or "").strip() or "default"

    def set_account(self, account_or_username):
        self.current_username = self._resolve_username(account_or_username)
        account = get_account(self.current_username) or {"username": self.current_username}
        set_active_account(account)
        self.engine.load_history()
        self._restore_latest_process_state()

    def _show_history_detail_popup(self, record):
        headers = ["Client", "PhilHealth No", "Employee Name", "Birthdate"]
        popup = SingleTablePopup(
            f"Historical Records: {record.get('month_year', '')}",
            headers,
            record.get("data_total", []),
            self.window(),
            tabs=[
                ("Active", record.get("data_total", [])),
                ("Missing", record.get("data_missing", [])),
                ("Newly Hired", record.get("data_new", [])),
            ],
        )
        popup.setStyleSheet(self._detail_style())
        self.detail_popups.append(popup)
        popup.destroyed.connect(lambda: self._forget_popup(popup))
        popup.show()
        popup.activateWindow()
        popup.raise_()

    def _show_current_detail_popup(self, title, headers, data):
        if not data:
            GlassDialog(self, "No Records", f"No metric records found to review for '{title}'.").exec()
            return
        popup = SingleTablePopup(title, headers, data, self.window())
        popup.setStyleSheet(self._detail_style())
        self.detail_popups.append(popup)
        popup.destroyed.connect(lambda: self._forget_popup(popup))
        popup.show()
        popup.activateWindow()
        popup.raise_()

    def _forget_popup(self, popup):
        if popup in self.detail_popups:
            self.detail_popups.remove(popup)

    def _restore_latest_process_state(self):
        if not hasattr(self, "engine") or not getattr(self.engine, "history_records", None):
            return

        latest_record = self.engine.history_records[-1]
        self._apply_record_to_process_view(latest_record)

    def _apply_record_to_process_view(self, record):
        if not record:
            return

        month_year = record.get("month_year", "Pending")
        self.engine.card_month.update_value(month_year)
        self.engine.card_total.update_value(record.get("total_count", 0))
        self.engine.card_missing.update_value(record.get("missing_count", 0))
        self.engine.card_new.update_value(record.get("new_count", 0))

        self.engine.cache_total_active = list(record.get("data_total", []))
        self.engine.cache_missing = list(record.get("data_missing", []))
        self.engine.cache_newly_hired = list(record.get("data_new", []))

        missing_by_client = {}
        for client, ph, name, birthdate in self.engine.cache_missing:
            missing_by_client.setdefault(client, []).append((ph, birthdate, name))

        added_by_client = {}
        for client, ph, name, birthdate in self.engine.cache_newly_hired:
            added_by_client.setdefault(client, []).append((ph, birthdate, name))

        self._populate_process_table(self.engine.missing_table, missing_by_client)
        self._populate_process_table(self.engine.newly_hired_table, added_by_client)
        self._populate_summary_table(
            [
                ("Total Active Staffs (Current Month)", record.get("total_count", 0)),
                ("Total Active Staffs (Previous Month Baseline)", record.get("previous_count", 0)),
                ("Total Missing Headcounts", record.get("missing_count", 0)),
                ("Total Newly Hired Headcounts", record.get("new_count", 0)),
            ]
        )
        self.progress_note_label.setText(f"Loaded latest upload: {month_year}")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.progress_percent_label.setText("100%")

    def _populate_process_table(self, table_widget, grouped_data):
        table_widget.setRowCount(0)
        row_idx = 0
        for client in sorted(grouped_data.keys(), key=lambda x: str(x).upper()):
            for ph, bd, name in grouped_data[client]:
                table_widget.insertRow(row_idx)
                items = [
                    QTableWidgetItem(str(client)),
                    QTableWidgetItem(str(ph)),
                    QTableWidgetItem(str(name)),
                    QTableWidgetItem(str(bd)),
                ]
                items[1].setTextAlignment(Qt.AlignCenter)
                items[3].setTextAlignment(Qt.AlignCenter)
                for col, item in enumerate(items):
                    item.setForeground(QColor("#e2e8f0"))
                    table_widget.setItem(row_idx, col, item)
                row_idx += 1

    def _populate_summary_table(self, metrics):
        self.engine.summary_table.setRowCount(0)
        for row_idx, (label, value) in enumerate(metrics):
            self.engine.summary_table.insertRow(row_idx)
            item_lbl = QTableWidgetItem(str(label))
            item_val = QTableWidgetItem(str(value))
            item_val.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_lbl.setForeground(QColor("#e2e8f0"))
            item_val.setForeground(QColor("#3b82f6"))
            self.engine.summary_table.setItem(row_idx, 0, item_lbl)
            self.engine.summary_table.setItem(row_idx, 1, item_val)

    def _detail_style(self):
        return """
            QDialog {
                background: qradialgradient(cx:0.2, cy:0.1, radius:1.2,
                                            stop:0 #102a24, stop:0.55 #081412, stop:1 #020408);
                border: 1px solid rgba(20, 184, 166, 0.28);
                border-radius: 16px;
            }
            QLabel {
                color: #e5e7eb;
                background: transparent;
                border: none;
                font-family: 'Segoe UI';
            }
            QPushButton {
                background: rgba(30, 41, 59, 0.82);
                border: 1px solid rgba(148, 163, 184, 0.24);
                border-radius: 10px;
                color: #e5e7eb;
                font: 800 12px 'Segoe UI';
            }
            QPushButton:hover {
                background: rgba(244, 63, 94, 0.72);
                border-color: rgba(244, 63, 94, 0.88);
                color: #ffffff;
            }
            QTableWidget {
                background: rgba(2, 6, 23, 0.48);
                alternate-background-color: rgba(15, 23, 42, 0.55);
                border: 1px solid rgba(148, 163, 184, 0.20);
                border-radius: 10px;
                color: #e5e7eb;
                gridline-color: rgba(148, 163, 184, 0.16);
                selection-background-color: rgba(20, 184, 166, 0.34);
                selection-color: #ffffff;
                font: 11px 'Segoe UI';
            }
            QTableWidget::item {
                color: #e5e7eb;
                padding: 5px 8px;
            }
            QHeaderView::section {
                background: rgba(2, 6, 23, 0.86);
                border: none;
                border-right: 1px solid rgba(148, 163, 184, 0.18);
                color: #f8fafc;
                font: 800 11px 'Segoe UI';
                padding: 8px;
            }
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
        """

    def _setup_ui(self):
        self.setStyleSheet(self._style())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        title = QLabel("PhilHealth Automation")
        title.setFont(QFont("Segoe UI", 17, QFont.Bold))
        title.setStyleSheet(AppStyles.PANEL_TITLE)
        layout.addWidget(title)

        tabs = QTabWidget()
        tabs.addTab(self._process_tab(), "Process")
        tabs.addTab(self._records_tab(), "Records Viewer")
        layout.addWidget(tabs, stretch=1)

    def _process_tab(self):
        tab = QWidget()
        tab.setStyleSheet("background: transparent; border: none;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        form_card = QFrame()
        form_card.setObjectName("GovCard")
        form_layout = QGridLayout(form_card)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setHorizontalSpacing(16)
        form_layout.setVerticalSpacing(12)

        self._add_form_row(form_layout, 0, "Source Directory", self.engine.src_input, self.engine.src_btn)
        self._add_form_row(form_layout, 1, "Save Directory", self.engine.save_input, self.engine.save_btn)
        self._add_form_row(form_layout, 2, "Output Base Name", self.engine.fn_input, None)
        self._add_period_row(form_layout, 3)

        layout.addWidget(form_card)

        self.engine.process_btn.setText("Start Processing & Reconciliation")
        self.engine.process_btn.setMinimumHeight(50)
        self.engine.process_btn.setStyleSheet(AppStyles.PRIMARY_BUTTON)
        try:
            self.engine.process_btn.clicked.disconnect()
        except RuntimeError:
            pass
        self.engine.process_btn.clicked.connect(self.start_processing)
        layout.addWidget(self.engine.process_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFixedHeight(24)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background: rgba(2, 6, 23, 0.62);
                border: 1px solid rgba(148, 163, 184, 0.20);
                border-radius: 8px;
                color: #f8fafc;
                text-align: center;
                padding: 0px;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #14b8a6,
                    stop:1 #3b82f6
                );
                border-radius: 8px;
            }
        """)

        progress_stack = QGridLayout()
        progress_stack.setContentsMargins(0, 0, 0, 0)
        progress_stack.setHorizontalSpacing(0)
        progress_stack.setVerticalSpacing(0)
        progress_stack.addWidget(self.progress_bar, 0, 0)

        self.progress_percent_label = QLabel("0%")
        self.progress_percent_label.setAlignment(Qt.AlignCenter)
        self.progress_percent_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.progress_percent_label.setStyleSheet(
            "color: #f8fafc; font-size: 12px; font-weight: 700; background: transparent;"
        )
        progress_stack.addWidget(self.progress_percent_label, 0, 0)
        layout.addLayout(progress_stack)

        self.progress_note_label = QLabel("Ready")
        self.progress_note_label.setStyleSheet(
            "color: #94a3b8; font-size: 11px; border: none; background: transparent;"
        )
        layout.addWidget(self.progress_note_label)

        metrics = QHBoxLayout()
        metrics.setSpacing(12)
        for card in [
            self.engine.card_month,
            self.engine.card_total,
            self.engine.card_missing,
            self.engine.card_new,
        ]:
            metrics.addWidget(card)
        layout.addLayout(metrics)
        layout.addStretch()
        return tab

    def start_processing(self):
        source_dir = self.engine.src_input.text().strip()
        save_dir = self.engine.save_input.text().strip()
        base_filename = self.engine.fn_input.text().strip()
        if not source_dir or not os.path.exists(source_dir) or not save_dir or not base_filename:
            GlassDialog(
                self,
                "PhilHealth Setup Needed",
                "Please select a valid source directory, save directory, and output base name.",
            ).exec()
            return

        if self.is_processing:
            return

        self.is_processing = True
        self.engine.process_btn.setEnabled(False)
        self.progress_note_label.setText("Starting reconciliation...")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_percent_label.setText("0%")
        QTimer.singleShot(50, self._run_processing)

    def _run_processing(self):
        try:
            self.controller.process(progress_callback=self._update_processing_progress)
        except Exception as exc:
            self.progress_note_label.setText("Finished with errors.")
            GlassDialog(self, "PhilHealth Processing Error", str(exc)).exec()
        else:
            self.progress_note_label.setText("Processing complete.")
        finally:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)
            self.progress_percent_label.setText("100%")
            self.engine.process_btn.setEnabled(True)
            self.is_processing = False

    def _update_processing_progress(self, percent, filename="", message=""):
        self.progress_bar.setRange(0, 100)
        value = max(0, min(100, int(percent)))
        self.progress_bar.setValue(value)
        self.progress_percent_label.setText(f"{value}%")
        if message:
            detail = message
        elif filename:
            detail = f"Working on {filename}"
        else:
            detail = "Processing PhilHealth records..."
        self.progress_note_label.setText(detail)
        QApplication.processEvents()

    def _render_history_grid(self):
        if not hasattr(self.engine, "history_grid_layout"):
            return

        while self.engine.history_grid_layout.count():
            child = self.engine.history_grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        col_count = 3
        records = list(reversed(getattr(self.engine, "history_records", [])))
        for idx, record in enumerate(records):
            row = idx // col_count
            col = idx % col_count
            card = HistoryCardWidget(record)
            card.delete_requested.connect(self._delete_history_record)
            card.opened.connect(self._show_history_detail_popup)
            self.engine.history_grid_layout.addWidget(card, row, col)

    def _save_history_record(self, record_data):
        record = dict(record_data)
        record.setdefault("created_at", datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.engine.history_records.append(record)
        try:
            active_account = get_active_account() or {}
            username = self.current_username or active_account.get("username") or "default"
            self.controller.save_history(username, record)
            self._render_history_grid()
        except Exception as exc:
            GlassDialog(self, "Save Error", f"Could not save history log.\n{exc}").exec()

    def _delete_history_record(self, record_id, month_year_label=None):
        record = next(
            (
                item
                for item in getattr(self.engine, "history_records", [])
                if item.get("id") == record_id
            ),
            None,
        )
        if record is None:
            return

        label = month_year_label or record.get("month_year", "this record")
        confirm = GlassDialog(
            self,
            "Delete Historical Record",
            f"Delete the historical record for {label}?\n\nThis cannot be undone.",
            buttons=[
                ("Cancel", lambda: confirm.reject(), False),
                ("Delete", lambda: confirm.accept(), True),
            ],
        )
        if confirm.exec() != QDialog.Accepted:
            return

        if self.selected_history_record_id == record_id:
            self.selected_history_record_id = None
        self.engine.history_records = [
            record for record in self.engine.history_records if record.get("id") != record_id
        ]
        try:
            self.controller.delete_history(record_id)
            self._render_history_grid()
            self._restore_latest_process_state()
        except Exception as exc:
            GlassDialog(self, "Delete Error", f"Could not delete history log.\n{exc}").exec()

    def _records_tab(self):
        tab = QWidget()
        tab.setStyleSheet("background: transparent; border: none;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("PhilHealth Records Viewer")
        title.setStyleSheet(AppStyles.CARD_HEADER)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        self.engine.tab_container.setObjectName("RecordsTabs")
        layout.addWidget(self.engine.tab_container, stretch=1)
        return tab

    def _add_form_row(self, layout, row, label_text, field, button):
        label = QLabel(label_text)
        label.setFixedWidth(120)
        layout.addWidget(label, row, 0)
        layout.addWidget(field, row, 1)

        if button is not None:
            button.setText("Browse")
            button.setFixedWidth(92)
            layout.addWidget(button, row, 2)
        else:
            spacer = QWidget()
            spacer.setFixedWidth(92)
            layout.addWidget(spacer, row, 2)

    def _add_period_row(self, layout, row):
        label = QLabel("Applicable Period")
        label.setFixedWidth(120)
        period = QWidget()
        period.setStyleSheet("background: transparent; border: none;")
        period_layout = QHBoxLayout(period)
        period_layout.setContentsMargins(0, 0, 0, 0)
        period_layout.setSpacing(10)
        period_layout.addWidget(self.engine.month_combo, stretch=2)
        period_layout.addWidget(self.engine.year_combo, stretch=1)

        layout.addWidget(label, row, 0)
        layout.addWidget(period, row, 1)

    def _style(self):
        return """
            QWidget {
                background: transparent;
                color: #e5e7eb;
                font-family: 'Segoe UI';
            }
            QFrame#GovCard {
                background: rgba(20, 43, 37, 0.64);
                border: 1px solid rgba(148, 163, 184, 0.22);
                border-radius: 10px;
            }
            QLabel {
                color: #cbd5e1;
                background: transparent;
                border: none;
                font: 600 12px 'Segoe UI';
            }
            QLineEdit, QComboBox {
                background: rgba(2, 6, 23, 0.56);
                border: 1px solid rgba(148, 163, 184, 0.24);
                border-radius: 7px;
                color: #e5e7eb;
                min-height: 34px;
                padding: 0 10px;
                font: 12px 'Segoe UI';
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: rgba(20, 184, 166, 0.72);
            }
            QPushButton {
                background: rgba(30, 41, 59, 0.72);
                border: 1px solid rgba(148, 163, 184, 0.28);
                border-radius: 8px;
                color: #e5e7eb;
                min-height: 34px;
                font: 700 12px 'Segoe UI';
                padding: 0 12px;
            }
            QPushButton:hover {
                background: rgba(51, 65, 85, 0.82);
                border-color: rgba(20, 184, 166, 0.38);
            }
            QPushButton#PrimaryButton,
            QPushButton:default {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #14b8c8, stop:1 #3b82f6);
                border: none;
                color: #ffffff;
            }
            QTabWidget::pane {
                background: rgba(8, 20, 18, 0.32);
                border: 1px solid rgba(148, 163, 184, 0.18);
                border-radius: 10px;
                top: -1px;
            }
            QTabBar::tab {
                background: rgba(15, 23, 42, 0.62);
                border: 1px solid rgba(148, 163, 184, 0.16);
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                color: #94a3b8;
                min-width: 130px;
                padding: 9px 16px;
                font: 700 12px 'Segoe UI';
            }
            QTabBar::tab:selected {
                background: rgba(20, 43, 37, 0.82);
                color: #e5e7eb;
                border-color: rgba(20, 184, 166, 0.34);
            }
            QTableWidget {
                background: rgba(2, 6, 23, 0.46);
                border: 1px solid rgba(148, 163, 184, 0.18);
                border-radius: 10px;
                color: #e5e7eb;
                gridline-color: rgba(148, 163, 184, 0.16);
                selection-background-color: rgba(20, 184, 166, 0.34);
            }
            QHeaderView::section {
                background: rgba(2, 6, 23, 0.74);
                border: none;
                border-right: 1px solid rgba(148, 163, 184, 0.18);
                color: #cbd5e1;
                font: 700 11px 'Segoe UI';
                padding: 7px 8px;
            }
            MetricCard, HistoryCard {
                background: rgba(20, 43, 37, 0.64);
                border: 1px solid rgba(148, 163, 184, 0.22);
                border-radius: 8px;
            }
            QScrollArea {
                background: transparent;
                border: none;
            }
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
                background: rgba(2, 6, 23, 0.18);
                border: none;
                border-radius: 6px;
                height: 12px;
                margin: 3px;
            }
            QScrollBar::handle:horizontal {
                background: rgba(148, 163, 184, 0.46);
                border-radius: 6px;
                min-width: 24px;
            }
            QScrollBar::handle:horizontal:hover {
                background: rgba(20, 184, 166, 0.72);
            }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal,
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: transparent;
                border: none;
                width: 0;
            }
        """
