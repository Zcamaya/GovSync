from PySide6.QtCore import Qt, QTimer, Signal, QSize
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtWidgets import QAbstractItemView

from constants.styles import AppStyles
from controllers.employee_records_controller import EmployeeRecordsController
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

        self.stats_panel = TrueGlassPanel(border_radius=16)
        stats_layout = QHBoxLayout(self.stats_panel)
        stats_layout.setContentsMargins(18, 18, 18, 18)
        stats_layout.setSpacing(12)
        self.stats_cards = []
        for label in ["Total Employees", "Total Clients", "Total Payroll Imports", "Last Imported Payroll"]:
            card = QFrame()
            card.setStyleSheet("background: rgba(15, 23, 42, 0.55); border: 1px solid rgba(255,255,255,0.08); border-radius: 14px;")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(12, 12, 12, 12)
            card_layout.setSpacing(6)
            title = QLabel(label)
            title.setStyleSheet("color: #cbd5e1; font-size: 12px;")
            value = QLabel("0")
            value.setStyleSheet("color: #34d399; font-size: 22px; font-weight: 700;")
            card_layout.addWidget(title)
            card_layout.addWidget(value)
            stats_layout.addWidget(card)
            self.stats_cards.append((title, value))
        layout.addWidget(self.stats_panel)

        filters_panel = TrueGlassPanel(border_radius=16)
        filters_layout = QHBoxLayout(filters_panel)
        filters_layout.setContentsMargins(16, 16, 16, 16)
        filters_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search employee")
        self.search_input.setStyleSheet("QLineEdit { background: rgba(15,23,42,0.75); color: white; border: 1px solid rgba(255,255,255,0.14); border-radius: 8px; padding: 8px 10px; }")
        filters_layout.addWidget(self.search_input, stretch=1)

        self.employer_combo = QComboBox()
        self.employer_combo.addItem("Employer")
        filters_layout.addWidget(self.employer_combo)

        self.client_combo = QComboBox()
        self.client_combo.addItem("Client")
        filters_layout.addWidget(self.client_combo)

        self.applicable_month_combo = QComboBox()
        self.applicable_month_combo.addItem("Applicable Month")
        filters_layout.addWidget(self.applicable_month_combo)

        # Style dropdowns to match screenshot: dark popup, teal selection
        combo_style = AppStyles.GLOBAL_DROPDOWN
        for cb in (self.employer_combo, self.client_combo, self.applicable_month_combo):
            cb.setStyleSheet(combo_style)
            cb.setFocusPolicy(Qt.NoFocus)
            try:
                view = cb.view()
                view.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
            except Exception as exc:
                print(f"Failed to style combo box view: {exc}")
            cb.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        layout.addWidget(filters_panel)

        self.table = QTableWidget(0, 3)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet(
            "QTableWidget { background: #071b1b; color: #dbeafe; border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; margin-right: 2px; }"
            " QHeaderView::section { background: #2b3744; color: #f8fafc; padding: 8px; border: none; font-weight: 700; }"
            " QTableWidget::item { padding: 6px 8px; border-bottom: 1px solid rgba(255,255,255,0.04); }"
            " QTableWidget::item:selected { background: #0f766e; color: #ffffff; }"
            " QTableWidget::item:alternate { background: #041516; }"
            " QTableWidget QScrollBar:vertical { background: rgba(15,23,42,0.48); width: 12px; border-radius: 6px; margin: 2px; }"
            " QTableWidget QScrollBar::handle:vertical { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #14b8a6, stop:1 #3b82f6); border-radius: 6px; min-height: 20px; }"
            " QTableWidget QScrollBar::handle:vertical:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2dd4bf, stop:1 #60a5fa); }",
        )
        self.table.setHorizontalHeaderLabels(["No.", "Client", "Employee Name"])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setWordWrap(True)
        # sensible default column widths - No. is fixed, others stretch proportionally
        self.table.setColumnWidth(0, 48)
        self.table.setSortingEnabled(False)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setMinimumHeight(200)
        self.table.verticalHeader().setDefaultSectionSize(36)
        self.table.cellDoubleClicked.connect(self._on_cell_double_clicked)
        layout.addWidget(self.table, stretch=1)

        paginator = QFrame()
        paginator.setMinimumHeight(52)
        paginator.setMaximumHeight(52)
        paginator_layout = QHBoxLayout(paginator)
        paginator_layout.setContentsMargins(4, 4, 4, 4)
        self.prev_button = QPushButton("← Previous")
        self.next_button = QPushButton("Next →")
        btn_style = """
            QPushButton {
                background: rgba(30, 41, 59, 0.82);
                color: #f8fafc;
                border: 1px solid rgba(148, 163, 184, 0.28);
                border-radius: 8px;
                padding: 8px 16px;
                font: 700 11px 'Segoe UI';
            }
            QPushButton:hover:!disabled {
                background: rgba(51, 65, 85, 0.92);
                border-color: rgba(148, 163, 184, 0.42);
                color: #ffffff;
            }
            QPushButton:disabled {
                color: rgba(226, 232, 240, 0.38);
                background: rgba(15, 23, 42, 0.5);
                border-color: rgba(148, 163, 184, 0.12);
            }
        """
        self.prev_button.setStyleSheet(btn_style)
        self.next_button.setStyleSheet(btn_style)
        self.page_label = QLabel("Page 1")
        self.page_label.setStyleSheet("color: #cbd5e1;")
        paginator_layout.addStretch()
        paginator_layout.addWidget(self.prev_button)
        paginator_layout.addWidget(self.page_label)
        paginator_layout.addWidget(self.next_button)
        paginator_layout.addStretch()
        layout.addWidget(paginator)

        self.loading_label = QLabel("Loading employees...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("color: #f8fafc; font-size: 13px; font-weight: 600; background: rgba(15, 23, 42, 0.68); border-radius: 8px; padding: 8px 12px;")
        self.loading_label.hide()
        layout.addWidget(self.loading_label)

    def _connect_signals(self):
        self.search_input.textChanged.connect(self._schedule_refresh)
        self.employer_combo.currentTextChanged.connect(self._schedule_refresh)
        self.client_combo.currentTextChanged.connect(self._schedule_refresh)
        self.applicable_month_combo.currentTextChanged.connect(self._schedule_refresh)
        self.prev_button.clicked.connect(self._previous_page)
        self.next_button.clicked.connect(self._next_page)

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
        employer_filter = self.employer_combo.currentText() if self.employer_combo.currentText() != "Employer" else ""
        search_text = self.search_input.text().strip()
        client_filter = self.client_combo.currentText() if self.client_combo.currentText() != "Client" else ""
        applicable_month_filter = self.applicable_month_combo.currentText() if self.applicable_month_combo.currentText() != "Applicable Month" else ""
        
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
        labels = ["total_employees", "total_clients", "total_imports", "last_imported"]
        for (title_label, value_label), key in zip(self.stats_cards, labels):
            value = stats.get(key, "")
            if key == "last_imported" and value:
                value = str(value)
            value_label.setText(str(value))

    def _populate_filters(self, employer_id):
        options = self.controller.get_filter_options(employer_id=employer_id) or {}
        self._set_combo_items(self.employer_combo, ["Employer"] + options.get("employers", []), self.employer_combo.currentText())
        self._set_combo_items(self.client_combo, ["Client"] + options.get("clients", []), self.client_combo.currentText())
        self._set_combo_items(self.applicable_month_combo, ["Applicable Month"] + options.get("applicable_months", []), self.applicable_month_combo.currentText())

    def _set_combo_items(self, combo, values, current_value):
        current = current_value if current_value in values else values[0] if values else ""
        combo.blockSignals(True)
        combo.clear()
        combo.addItems(values)
        combo.setCurrentText(current)
        combo.blockSignals(False)

    def _populate_table(self, employees):
        self.table.setRowCount(0)
        self._current_employee_rows = []
        if not employees:
            self.table.setRowCount(1)
            empty_item = QTableWidgetItem("No records found")
            empty_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, 0, empty_item)
            self.table.setSpan(0, 0, 1, self.table.columnCount())
            return

        self.table.setRowCount(len(employees))
        self._current_employee_rows = employees
        search_text = self.search_input.text().strip().lower()
        
        for row_index, employee in enumerate(employees):
            employee_name = " ".join(
                filter(
                    None,
                    [
                        employee.get("lastname", ""),
                        employee.get("firstname", ""),
                        employee.get("middlename", ""),
                    ],
                )
            ).strip()
            values = [
                str((self.current_page - 1) * self.page_size + row_index + 1),
                employee.get("client", ""),
                employee_name,
            ]
            for col_idx, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if search_text and search_text in str(value).lower():
                    item.setBackground(QColor(20, 100, 90))  # Teal highlight
                if col_idx in (1, 2):
                    item.setToolTip(str(value))
                self.table.setItem(row_index, col_idx, item)
            self.table.setRowHeight(row_index, 38)

    def _show_details(self, employee):
        if not employee:
            return
        employer_id = self.employer_id or (get_active_account() or {}).get("employer_name") or None
        employee_id = employee.get("employee_id", "")
        sss_number = employee.get("sss_number", "")
        history = self.controller.get_employee_payroll_history(employer_id=employer_id, employee_id=employee_id, sss_number=sss_number)
        account = get_active_account() or {}
        dialog = EmployeeDetailsDialog(employee, history, account, self)
        dialog.exec()

    def _on_cell_double_clicked(self, row, column):
        employees = getattr(self, "_current_employee_rows", [])
        if row < 0 or row >= len(employees):
            return
        self._show_details(employees[row])

    def _update_pagination(self, total_count):
        self.page_label.setText(f"Page {self.current_page}")
        self.prev_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled((self.current_page * self.page_size) < total_count)

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
            QScrollBar:vertical {
                background: rgba(15, 23, 42, 0.28);
                width: 10px;
                border-radius: 5px;
                margin: 2px 0;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #14b8a6, stop:1 #3b82f6);
                border-radius: 5px;
                min-height: 24px;
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2dd4bf, stop:1 #60a5fa);
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
                border: none;
            }
        """)
        
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
                ("Employer ID", self.account.get("employer_id", "") or employee.get("employer_id", "") or employee.get("company_id", "") or ""),
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
                history_panel = TrueGlassPanel(border_radius=12)
                history_layout = QVBoxLayout(history_panel)
                history_layout.setContentsMargins(14, 12, 14, 12)
                history_layout.setSpacing(10)
                
                history_title = QLabel("Payroll History")
                history_title.setStyleSheet(AppStyles.CARD_HEADER)
                history_layout.addWidget(history_title)
                
                history_table = QTableWidget(0, 9)
                history_table.setColumnCount(9)
                history_table.setHorizontalHeaderLabels([
                    "Applicable Month", "FDATE", "TDATE", "Client", "PHIC", "SSS", "PAGIBIG", "PAGIBIG LOANS", "SSS LOANS"
                ])
                history_table.setEditTriggers(QTableWidget.NoEditTriggers)
                history_table.setAlternatingRowColors(True)
                history_table.setMinimumHeight(220)
                history_table.verticalHeader().setVisible(False)
                history_table.setSelectionBehavior(QTableWidget.SelectRows)
                history_table.setSelectionMode(QTableWidget.SingleSelection)
                history_table.setStyleSheet(AppStyles.HISTORY_SURFACE)
                
                history_table.setRowCount(len(history))
                for row_idx, item in enumerate(history):
                    values = [
                        item.get("applicable_month", ""),
                        item.get("from_date", ""),
                        item.get("to_date", ""),
                        item.get("client", ""),
                        item.get("philhealth", ""),
                        item.get("sss", ""),
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
                history_table.setColumnWidth(0, 120)  # Applicable Month
                history_table.setColumnWidth(1, 100)  # FDATE
                history_table.setColumnWidth(2, 100)  # TDATE
                history_table.setColumnWidth(3, 140)  # Client
                history_table.setColumnWidth(4, 80)   # PHIC
                history_table.setColumnWidth(5, 80)   # SSS
                history_table.setColumnWidth(6, 100)  # PAGIBIG
                history_table.setColumnWidth(7, 120)  # PAGIBIG LOANS
                history_table.setColumnWidth(8, 100)  # SSS LOANS
                
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
