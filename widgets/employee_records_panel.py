from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from constants.styles import AppStyles
from controllers.employee_records_controller import EmployeeRecordsController
from widgets.employee_records_header import EmployeeRecordsHeader
from widgets.employee_records_paginator import EmployeeRecordsPaginator
from widgets.employee_records_table import EmployeeRecordsTable
from widgets.glass_panel import TrueGlassPanel
from widgets.glass_dialog import GlassDialog
from core.session_manager import get_active_account
from shared.ui import set_exit_icon


class EmployeeRecordsPanel(QWidget):
    def __init__(self, controller: EmployeeRecordsController | None = None, parent=None):
        super().__init__(parent)
        self.controller = controller or EmployeeRecordsController()
        self.current_page = 1
        self.page_size = 100
        self.employer_id = None
        self._pending_refresh = False
        self._build_ui()
        self._connect_signals()
        self.refresh_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        self.header = EmployeeRecordsHeader(self)
        layout.addWidget(self.header)

        self.table = EmployeeRecordsTable(self)
        self.table.cellDoubleClicked.connect(self._on_cell_double_clicked)
        self.table.setStyleSheet(
            AppStyles.TABLE_BASE
            + AppStyles.TABLE_SCROLLBAR
            + """
            QTableWidget { border: none; border-radius: 14px; }
            QTableWidget::viewport { border-radius: 14px; }
        """
        )
        layout.addWidget(self.table, stretch=1)

        self.paginator = EmployeeRecordsPaginator(self)
        layout.addWidget(self.paginator)

        self.loading_label = QLabel("Loading employees...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet(
            "color: #f8fafc; font-size: 13px; font-weight: 600; background: rgba(15, 23, 42, 0.68); border-radius: 8px; padding: 8px 12px;"
        )
        self.loading_label.hide()
        layout.addWidget(self.loading_label)

    def _connect_signals(self):
        self.header.search_input.textChanged.connect(self._schedule_refresh)
        self.header.employer_combo.currentTextChanged.connect(self._schedule_refresh)
        self.header.client_combo.currentTextChanged.connect(self._schedule_refresh)
        self.header.applicable_month_combo.currentTextChanged.connect(self._schedule_refresh)
        self.paginator.prev_button.clicked.connect(self._previous_page)
        self.paginator.next_button.clicked.connect(self._next_page)

    def set_account(self, account):
        # Refresh data when account changes (shows all employees across all accounts)
        self.refresh_data()

    def _schedule_refresh(self):
        self._pending_refresh = True
        QTimer.singleShot(250, self.refresh_data)

    def refresh_data(self):
        if self._pending_refresh:
            self._pending_refresh = False
        self._show_loading(True)
        self._load_data_async()

    def _load_data_async(self):
        account = get_active_account() or {}
        employer_id = None  # Show all employees from all accounts
        employer_filter = self.header.employer_combo.currentText() if self.header.employer_combo.currentText() != "Employer" else ""
        search_text = self.header.search_input.text().strip()
        client_filter = self.header.client_combo.currentText() if self.header.client_combo.currentText() != "Client" else ""
        applicable_month_filter = self.header.applicable_month_combo.currentText() if self.header.applicable_month_combo.currentText() != "Applicable Month" else ""
        
        sort_by = "lastname"
        sort_order = "asc"

        employees, total_count = self.controller.list_employees(
            employer_id=employer_id,
            search_text=search_text,
            client_filter=client_filter,
            applicable_month_filter=applicable_month_filter,
            employer_filter=employer_filter,
            lastname_filter="",
            sort_by=sort_by,
            sort_order=sort_order,
            page=self.current_page,
            page_size=self.page_size,
        )
        self._populate_filters(employer_id)

        self._populate_table(employees)
        self._populate_stats(employer_id)
        self._update_pagination(total_count)
        self._show_loading(False)

    def _populate_stats(self, employer_id):
        stats = self.controller.get_statistics(employer_id=employer_id)
        self.header.set_stats(stats)

    def _populate_filters(self, employer_id):
        options = self.controller.get_filter_options(employer_id=employer_id) or {}
        self.header.set_filter_options(options)

    def _populate_table(self, employees):
        search_text = self.header.search_input.text().strip().lower()
        self.table.populate(
            employees,
            search_text=search_text,
            page=self.current_page,
            page_size=self.page_size,
        )

    def _show_details(self, employee):
        if not employee:
            return
        employer_id = self.employer_id or (get_active_account() or {}).get("employer_id") or (get_active_account() or {}).get("employer_name") or None
        employee_id = employee.get("employee_id", "")
        sss_number = employee.get("sss_number", "")
        history = self.controller.get_employee_payroll_history(employer_id=employer_id, employee_id=employee_id, sss_number=sss_number)
        account = get_active_account() or {}
        dialog = EmployeeDetailsDialog(employee, history, account, self)
        dialog.exec()

    def _on_cell_double_clicked(self, row, column):
        employee = self.table.get_current_employee(row)
        self._show_details(employee)

    def _update_pagination(self, total_count):
        self.paginator.update_page(self.current_page)
        self.paginator.set_buttons_enabled(
            prev_enabled=self.current_page > 1,
            next_enabled=(self.current_page * self.page_size) < total_count,
        )

    def _previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_data()

    def _next_page(self):
        self.current_page += 1
        self.refresh_data()

    def _show_loading(self, visible):
        self.loading_label.setVisible(visible)
        self.table.setVisible(not visible)


class EmployeeDetailsDialog(QDialog):
    def __init__(self, employee, history, account=None, parent=None):
        super().__init__(parent)
        self.account = account or {}
        self.setWindowTitle("Employee Details")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        self.resize(900, 750)
        
        self.setStyleSheet(AppStyles.DIALOG_BASE)
        
        # Validate Employee ID and SSS
        employee_id = employee.get("employee_id", "").strip()
        sss_number = employee.get("sss_number", "").strip()
        has_valid_id = bool(employee_id)
        has_valid_sss = bool(sss_number)
        full_name = " ".join(
            filter(None, [
                employee.get("firstname", ""),
                employee.get("middlename", ""),
                employee.get("lastname", ""),
            ])
        ).strip() or employee.get("employee_key", "")

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(1, 1, 1, 1)
        outer_layout.setSpacing(0)

        card = QFrame()
        card.setObjectName("DialogCard")
        outer_layout.addWidget(card)

        main_layout = QVBoxLayout(card)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(14)

        # Header with title and close button
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        title = QLabel(f"Employee Details: {full_name}")
        title.setObjectName("DialogTitle")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        close_btn = QPushButton()
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(Qt.PointingHandCursor)
        set_exit_icon(close_btn, "#93c5fd", 11)
        close_btn.setStyleSheet(AppStyles.SQUARE_CLOSE_BUTTON)
        close_btn.clicked.connect(self.reject)
        header_layout.addWidget(close_btn)
        
        main_layout.addLayout(header_layout)

        # Validation warning if ID or SSS is missing
        if not has_valid_id or not has_valid_sss:
            warning = QLabel()
            warning_text = []
            if not has_valid_id:
                warning_text.append("Employee ID")
            if not has_valid_sss:
                warning_text.append("SSS Number")
            warning.setText(f"⚠ Missing: {', '.join(warning_text)}")
            warning.setStyleSheet("color: #fbbf24; font-size: 11px; font-weight: 600;")
            main_layout.addWidget(warning)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
        """ + AppStyles.SCROLLBAR)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(12)
        content_layout.setContentsMargins(0, 0, 0, 0)

        if history or employee:
            # Basic Information Panel
            basic = TrueGlassPanel(border_radius=12)
            basic_layout = QVBoxLayout(basic)
            basic_layout.setContentsMargins(14, 12, 14, 12)
            basic_layout.setSpacing(8)
            
            basic_title = QLabel("Basic Information")
            basic_title.setStyleSheet(AppStyles.CARD_HEADER)
            basic_layout.addWidget(basic_title)
            
            grid_basic = QVBoxLayout()
            grid_basic.setSpacing(6)
            for label_text, field in [
                ("Employee ID", employee.get("employee_id", "")),
                ("Full Name", full_name),
                ("Birthdate", employee.get("birthdate", "")),
                ("Position", employee.get("position", "")),
                ("Date Hired", employee.get("date_hired", "")),
                ("Client", employee.get("client", "")),
            ]:
                row = QHBoxLayout()
                row.setSpacing(10)
                label = QLabel(f"{label_text}:")
                label.setStyleSheet("color: #cbd5e1; font: 600 11px 'Segoe UI'; min-width: 100px;")
                value = QLabel(str(field))
                value.setStyleSheet("color: #e5e7eb; font: 11px 'Segoe UI';")
                value.setWordWrap(True)
                row.addWidget(label)
                row.addWidget(value, stretch=1)
                grid_basic.addLayout(row)
            
            basic_layout.addLayout(grid_basic)
            content_layout.addWidget(basic)

            # Government Information Panel
            gov = TrueGlassPanel(border_radius=12)
            gov_layout = QVBoxLayout(gov)
            gov_layout.setContentsMargins(14, 12, 14, 12)
            gov_layout.setSpacing(8)
            
            gov_title = QLabel("Government Information")
            gov_title.setStyleSheet(AppStyles.CARD_HEADER)
            gov_layout.addWidget(gov_title)
            
            grid_gov = QVBoxLayout()
            grid_gov.setSpacing(6)
            for label_text, field in [
                ("SSS Number", employee.get("sss_number", "")),
                ("Pag-IBIG Number", employee.get("pagibig_number", "")),
                ("PhilHealth Number", employee.get("philhealth_number", "")),
                ("TIN Number", employee.get("tin_number", "")),
            ]:
                row = QHBoxLayout()
                row.setSpacing(10)
                label = QLabel(f"{label_text}:")
                label.setStyleSheet("color: #cbd5e1; font: 600 11px 'Segoe UI'; min-width: 100px;")
                value = QLabel(str(field))
                value.setStyleSheet("color: #e5e7eb; font: 11px 'Segoe UI';")
                row.addWidget(label)
                row.addWidget(value, stretch=1)
                grid_gov.addLayout(row)
            
            gov_layout.addLayout(grid_gov)
            content_layout.addWidget(gov)

            # Employer Information Panel
            employer = TrueGlassPanel(border_radius=12)
            employer_layout = QVBoxLayout(employer)
            employer_layout.setContentsMargins(14, 12, 14, 12)
            employer_layout.setSpacing(8)

            employer_title = QLabel("Employer Information")
            employer_title.setStyleSheet(AppStyles.CARD_HEADER)
            employer_layout.addWidget(employer_title)

            grid_employer = QVBoxLayout()
            grid_employer.setSpacing(6)
            employer_fields = [
                ("Employer Name", self.account.get("employer_name", "") or employee.get("employer_name", "") or employee.get("client", "") or ""),
                ("Company", employee.get("company", "") or employee.get("client", "") or ""),
            ]
            for label_text, field in employer_fields:
                row = QHBoxLayout()
                row.setSpacing(10)
                label = QLabel(f"{label_text}:")
                label.setStyleSheet("color: #cbd5e1; font: 600 11px 'Segoe UI'; min-width: 100px;")
                value = QLabel(str(field))
                value.setStyleSheet("color: #e5e7eb; font: 11px 'Segoe UI';")
                value.setWordWrap(True)
                row.addWidget(label)
                row.addWidget(value, stretch=1)
                grid_employer.addLayout(row)

            employer_layout.addLayout(grid_employer)
            content_layout.addWidget(employer)

            # Payroll Information Panel
            payroll = TrueGlassPanel(border_radius=12)
            payroll_layout = QVBoxLayout(payroll)
            payroll_layout.setContentsMargins(14, 12, 14, 12)
            payroll_layout.setSpacing(8)
            
            payroll_title = QLabel("Payroll Information")
            payroll_title.setStyleSheet(AppStyles.CARD_HEADER)
            payroll_layout.addWidget(payroll_title)
            
            grid_payroll = QVBoxLayout()
            grid_payroll.setSpacing(6)
            for label_text, field in [
                ("Basic Rate", employee.get("basic_rate", "")),
                ("Billing Rate", employee.get("billing_rate", "")),
                ("SSS", employee.get("sss", "")),
                ("Employee Share", employee.get("employee_share", "")),
                ("Employer Share", employee.get("employer_share", "")),
                ("Pag-IBIG", employee.get("pagibig", "")),
                ("PhilHealth", employee.get("philhealth", "")),
                ("SSS Loan", employee.get("sss_loan", "")),
                ("Pag-IBIG Loan", employee.get("pagibig_loan", "")),
                ("CTR", employee.get("ctr", "")),
            ]:
                row = QHBoxLayout()
                row.setSpacing(10)
                label = QLabel(f"{label_text}:")
                label.setStyleSheet("color: #cbd5e1; font: 600 11px 'Segoe UI'; min-width: 100px;")
                value = QLabel(str(field))
                value.setStyleSheet("color: #e5e7eb; font: 11px 'Segoe UI';")
                row.addWidget(label)
                row.addWidget(value, stretch=1)
                grid_payroll.addLayout(row)
            
            payroll_layout.addLayout(grid_payroll)
            content_layout.addWidget(payroll)

            # Payroll History Panel
            if history:
                # sort history so latest month is on top; prefer from_date then applicable_month
                try:
                    sorted_history = sorted(
                        history,
                        key=lambda i: (i.get("from_date") or i.get("applicable_month") or ""),
                        reverse=True,
                    )
                except Exception:
                    sorted_history = list(reversed(history))

                history_panel = TrueGlassPanel(border_radius=12)
                history_layout = QVBoxLayout(history_panel)
                history_layout.setContentsMargins(14, 12, 14, 12)
                history_layout.setSpacing(10)

                history_title = QLabel("Payroll History")
                history_title.setStyleSheet(AppStyles.CARD_HEADER)
                history_layout.addWidget(history_title)

                # Columns: Month, FDATE, TDATE, SSS, PHILHEALTH, PAGIBIG, PAGIBIG LOANS, SSS LOANS
                history_table = QTableWidget(0, 8)
                history_table.setColumnCount(8)
                history_table.setHorizontalHeaderLabels([
                    "Month", "FDATE", "TDATE", "SSS", "PHILHEALTH", "PAGIBIG", "PAGIBIG LOANS", "SSS LOANS"
                ])
                history_table.setEditTriggers(QTableWidget.NoEditTriggers)
                history_table.setAlternatingRowColors(True)
                history_table.setMinimumHeight(220)
                history_table.verticalHeader().setVisible(False)
                history_table.setSelectionBehavior(QTableWidget.SelectRows)
                history_table.setSelectionMode(QTableWidget.SingleSelection)
                history_table.setStyleSheet(
                    AppStyles.TABLE_BASE
                    + AppStyles.TABLE_SCROLLBAR
                    + """
                    QHeaderView::section {
                        background: rgba(2, 6, 23, 0.78);
                        color: #f8fafc;
                        padding: 8px;
                        border: none;
                        font-weight: 700;
                    }
                    QTableWidget::item:selected {
                        background: rgba(20, 184, 166, 0.24);
                        color: #ffffff;
                    }
                    QTableWidget::item:alternate {
                        background: rgba(2, 6, 23, 0.34);
                    }
                """
                )

                history_table.setRowCount(len(sorted_history))
                for row_idx, item in enumerate(sorted_history):
                    values = [
                        item.get("applicable_month", ""),
                        item.get("from_date", ""),
                        item.get("to_date", ""),
                        item.get("sss", ""),
                        item.get("philhealth", ""),
                        item.get("pagibig", ""),
                        item.get("pagibig_loan", ""),
                        item.get("sss_loan", ""),
                    ]
                    for col_idx, value in enumerate(values):
                        table_item = QTableWidgetItem(str(value) if value else "")
                        table_item.setFlags(table_item.flags() & ~Qt.ItemIsEditable)
                        history_table.setItem(row_idx, col_idx, table_item)
                    history_table.setRowHeight(row_idx, 30)

                # Adjust column widths
                history_table.setColumnWidth(0, 120)  # Month
                history_table.setColumnWidth(1, 100)  # FDATE
                history_table.setColumnWidth(2, 100)  # TDATE
                history_table.setColumnWidth(3, 100)  # SSS
                history_table.setColumnWidth(4, 100)  # PHILHEALTH
                history_table.setColumnWidth(5, 100)  # PAGIBIG
                history_table.setColumnWidth(6, 120)  # PAGIBIG LOANS
                history_table.setColumnWidth(7, 100)  # SSS LOANS

                history_layout.addWidget(history_table, stretch=1)
                content_layout.addWidget(history_panel)

        content_layout.addStretch()
        scroll.setWidget(content)
        main_layout.addWidget(scroll, stretch=1)

        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 8, 0, 0)
        button_layout.setSpacing(10)
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.setFixedHeight(36)
        close_button.setMinimumWidth(100)
        close_button.setStyleSheet(AppStyles.DIALOG_CLOSE_BUTTON)
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)
