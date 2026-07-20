import os
import threading

from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QListWidget,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from constants.styles import AppStyles
from services.auth_manager import get_active_account
from services.sss_engine import get_default_month_and_year, get_months_list, get_years_list
from controllers.payroll_controller import PayrollController
from shared.helpers.account_state import account_state_path, resolve_account_username
from shared.helpers.json_state import load_json_dict, save_json_dict
from widgets.glass_dialog import GlassDialog


class PayrollWorker(QThread):
    progress = Signal(int, str)
    finished = Signal(bool, str, int)
    confirm_overwrite = Signal(object)

    def __init__(self, files, controller=None, applicable_month="", import_data=True, generate_sheets=None, parent=None):
        super().__init__(parent)
        self.files = files
        self.controller = controller
        self.applicable_month = applicable_month
        self.import_data = import_data
        self.generate_sheets = generate_sheets or ["PHIC", "HDMF", "SSS", "HDMF_LOANS", "SSS_LOANS"]
        self.overwrite_event = threading.Event()
        self.overwrite_decision = False

    def run(self):
        total = len(self.files)
        errors = []
        total_hdmf = 0

        for index, path in enumerate(self.files, start=1):
            filename = os.path.basename(path)
            self.progress.emit(int((index / total) * 100), filename)

            if filename.startswith("~$"):
                errors.append(f"{filename}: Skipped temporary Excel file.")
                continue

            try:
                plan = self.controller.build_import_plan(
                    path,
                    applicable_month=self.applicable_month,
                    progress_callback=self.progress.emit,
                )
                if self.import_data:
                    self.overwrite_decision = False
                    plan = self.controller.build_import_plan(
                        path,
                        applicable_month=self.applicable_month,
                        progress_callback=self.progress.emit,
                    )
                    if plan.existing_import is not None:
                        self.confirm_overwrite.emit({"plan": plan, "exact_duplicate": True})
                        self.overwrite_event.wait(timeout=300)
                        self.overwrite_event.clear()
                        if not self.overwrite_decision:
                            errors.append(f"{filename}: This exact workbook has already been imported.")
                            continue
                    elif plan.existing_payroll is not None:
                        self.confirm_overwrite.emit({"plan": plan, "exact_duplicate": False})
                        self.overwrite_event.wait(timeout=300)
                        self.overwrite_event.clear()
                        if not self.overwrite_decision:
                            errors.append(f"{filename}: Skipped because the payroll already exists.")
                            continue
                else:
                    plan = None
                    self.overwrite_decision = True

                success, message, hdmf_count = self.controller.process_file(
                    path,
                    progress_callback=self.progress.emit,
                    applicable_month=self.applicable_month,
                    plan=plan,
                    overwrite=self.overwrite_decision,
                    import_data=self.import_data,
                    generate_sheets=self.generate_sheets,
                )
                total_hdmf += hdmf_count
                if not success:
                    errors.append(f"{filename}: {message}")
            except Exception as exc:
                errors.append(f"{filename}: {exc}")

        if errors:
            self.finished.emit(False, "Errors occurred in:\n" + "\n".join(errors), total_hdmf)
        else:
            self.finished.emit(True, "All files processed successfully!", total_hdmf)


class EarningsPanel(QWidget):
    def __init__(self, parent=None, controller=None, dashboard_service=None):
        super().__init__(parent)
        self.selected_files = []
        self.controller = controller or PayrollController()
        self.dashboard_service = dashboard_service
        self.current_username = resolve_account_username(get_active_account() or {})
        self.worker = None
        self._setup_ui()
        self._load_state()

    def set_account(self, account):
        self.current_username = resolve_account_username(account)
        self._load_state()

    def _setup_ui(self):
        self.setStyleSheet("background: transparent;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(AppStyles.PANEL_SPACING)

        title = QLabel("Earnings Automation")
        title.setFont(QFont("Segoe UI", 17, QFont.Bold))
        title.setStyleSheet(AppStyles.PANEL_TITLE)
        main_layout.addWidget(title)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_widget.setAlternatingRowColors(False)
        self.list_widget.setStyleSheet("""
            QListWidget {
                background: rgba(20, 43, 37, 0.64);
                border: 1px solid rgba(148, 163, 184, 0.22);
                border-radius: 10px;
                color: #dbeafe;
                font: 12px 'Segoe UI';
                padding: 10px;
                outline: none;
            }
            QListWidget::item {
                border: none;
                border-radius: 8px;
                padding: 8px 10px;
                margin: 2px 0;
            }
            QListWidget::item:selected {
                background: rgba(16, 185, 129, 0.22);
                color: #ecfdf5;
            }
        """)
        main_layout.addWidget(self.list_widget, stretch=1)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(24)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background: rgba(2, 6, 23, 0.62);
                border: 1px solid rgba(148, 163, 184, 0.20);
                border-radius: 8px;
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
        progress_stack.addWidget(self.progress_bar, 0, 0)
        self.progress_percent_label = QLabel("0%")
        self.progress_percent_label.setAlignment(Qt.AlignCenter)
        self.progress_percent_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.progress_percent_label.setStyleSheet(
            "color: #f8fafc; font-size: 12px; font-weight: 700; background: transparent;"
        )
        progress_stack.addWidget(self.progress_percent_label, 0, 0)
        main_layout.addLayout(progress_stack)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(
            "color: #94a3b8; font-size: 11px; border: none; background: transparent;"
        )
        main_layout.addWidget(self.status_label)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(14)

        self.btn_add_file = self._secondary_button("Add File")
        self.btn_add_file.clicked.connect(self.add_files)

        self.btn_add_folder = self._secondary_button("Add Folder")
        self.btn_add_folder.clicked.connect(self.add_folder)

        self.btn_remove = self._secondary_button("Remove")
        self.btn_remove.clicked.connect(self.remove_selected)

        button_layout.addWidget(self.btn_add_file)
        button_layout.addWidget(self.btn_add_folder)
        button_layout.addWidget(self.btn_remove)
        main_layout.addLayout(button_layout)

        month_label = QLabel("Applicable Month:")
        month_label.setStyleSheet("color: #94a3b8; font-size: 11px;")
        self.month_combo = QComboBox()
        self.month_combo.setStyleSheet(AppStyles.GLOBAL_DROPDOWN)
        self.month_combo.addItems(get_months_list())
        default_month, default_year = get_default_month_and_year()
        self.month_combo.setCurrentText(default_month)

        year_label = QLabel("Year:")
        year_label.setStyleSheet("color: #94a3b8; font-size: 11px;")
        self.year_combo = QComboBox()
        self.year_combo.setStyleSheet(AppStyles.GLOBAL_DROPDOWN)
        self.year_combo.addItems(get_years_list())
        self.year_combo.setCurrentText(default_year)

        month_row = QHBoxLayout()
        month_row.setSpacing(10)
        month_row.addWidget(month_label)
        month_row.addWidget(self.month_combo)
        month_row.addWidget(year_label)
        month_row.addWidget(self.year_combo)
        month_row.addStretch()
        main_layout.addLayout(month_row)

        self.btn_start = QPushButton("Start Processing")
        self.btn_start.setCursor(Qt.PointingHandCursor)
        self.btn_start.setMinimumHeight(50)
        self.btn_start.setStyleSheet(AppStyles.PRIMARY_BUTTON)
        self.btn_start.clicked.connect(self.start_processing)
        main_layout.addWidget(self.btn_start)

    def _show_import_confirmation(self):
        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        dialog.setAttribute(Qt.WA_TranslucentBackground)
        dialog.setFixedSize(520, 420)
        dialog.setStyleSheet(AppStyles.DIALOG_BASE + "QCheckBox { color: #e2e8f0; }")

        outer = QFrame(dialog)
        outer.setObjectName("DialogCard")
        outer.setGeometry(0, 0, 520, 420)

        layout = QVBoxLayout(outer)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(16)

        title = QLabel("Import Confirmation")
        title.setStyleSheet("color: #f8fafc; font-size: 18px; font-weight: 700;")
        layout.addWidget(title)

        description = QLabel(
            "Choose whether to update the database and separately select which sheets to generate."
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: #cbd5e1; font-size: 13px;")
        layout.addWidget(description)

        self.import_data_checkbox = QCheckBox("Import data and update database")
        self.import_data_checkbox.setChecked(True)
        self.import_data_checkbox.setStyleSheet("QCheckBox { font-size: 13px; }")
        layout.addWidget(self.import_data_checkbox)

        sheet_section_label = QLabel("Generate Sheets")
        sheet_section_label.setStyleSheet("color: #f8fafc; font-size: 13px; font-weight: 700;")
        layout.addWidget(sheet_section_label)

        # Master enable checkbox for sheet generation (controls per-sheet checkboxes)
        self.enable_sheets_checkbox = QCheckBox("Enable sheet generation")
        self.enable_sheets_checkbox.setChecked(True)
        self.enable_sheets_checkbox.setStyleSheet("QCheckBox { font-size: 13px; }")
        layout.addWidget(self.enable_sheets_checkbox)

        self.sheet_checkboxes = []
        sheet_labels = ["PHIC", "HDMF", "SSS", "HDMF LOANS", "SSS LOANS"]
        sheet_layout = QVBoxLayout()
        sheet_layout.setContentsMargins(16, 0, 0, 0)
        for label in sheet_labels:
            checkbox = QCheckBox(label)
            checkbox.setChecked(True)
            checkbox.setStyleSheet("QCheckBox { font-size: 13px; }")
            sheet_layout.addWidget(checkbox)
            self.sheet_checkboxes.append((label, checkbox))
        layout.addLayout(sheet_layout)

        def update_sheet_enable():
            enabled = bool(self.enable_sheets_checkbox.isChecked())
            for _, checkbox in self.sheet_checkboxes:
                checkbox.setEnabled(enabled)

        self.enable_sheets_checkbox.stateChanged.connect(lambda _: update_sheet_enable())
        update_sheet_enable()

        button_row = QHBoxLayout()
        button_row.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedHeight(40)
        cancel_btn.setStyleSheet(AppStyles.SECONDARY_BUTTON)
        ok_btn = QPushButton("Continue")
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.setFixedHeight(40)
        ok_btn.setStyleSheet(AppStyles.PRIMARY_BUTTON)
        button_row.addWidget(cancel_btn)
        button_row.addWidget(ok_btn)
        layout.addLayout(button_row)

        result = {}

        def accept_dialog():
            # If sheet generation master is unchecked, return empty generate_sheets
            if self.enable_sheets_checkbox.isChecked():
                selected = [key.replace(" ", "_") for key, checkbox in self.sheet_checkboxes if checkbox.isChecked()]
            else:
                selected = []
            result["import_data"] = self.import_data_checkbox.isChecked()
            result["generate_sheets"] = selected
            dialog.accept()

        def cancel_dialog():
            dialog.reject()

        ok_btn.clicked.connect(accept_dialog)
        cancel_btn.clicked.connect(cancel_dialog)

        if dialog.exec() == QDialog.Accepted:
            return result
        return None

    def _secondary_button(self, text):
        button = QPushButton(text)
        button.setCursor(Qt.PointingHandCursor)
        button.setMinimumHeight(38)
        button.setStyleSheet(AppStyles.SECONDARY_BUTTON)
        return button

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Excel Files", "", "Excel Files (*.xlsx)"
        )
        self._add_paths(files)

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if not folder:
            return

        files = [
            os.path.join(folder, filename)
            for filename in sorted(os.listdir(folder))
            if filename.lower().endswith(".xlsx")
        ]
        self._add_paths(files)

    def _add_paths(self, paths):
        for file_path in paths:
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)
                self.list_widget.addItem(os.path.basename(file_path))

        self.status_label.setText(f"{len(self.selected_files)} file(s) ready")
        self._save_state()

    def remove_selected(self):
        for item in reversed(self.list_widget.selectedItems()):
            index = self.list_widget.row(item)
            self.list_widget.takeItem(index)
            self.selected_files.pop(index)

        self.status_label.setText(f"{len(self.selected_files)} file(s) ready")
        self._save_state()

    def start_processing(self):
        if not self.selected_files:
            GlassDialog(self, "Notice", "Please add files first.").exec()
            return

        self._set_processing_enabled(False)
        self.progress_bar.setValue(0)
        self.progress_percent_label.setText("0%")
        account = get_active_account() or {}
        employer_name = str(account.get("employer_name") or account.get("username") or "").strip() or "Current Employer"
        self.status_label.setText(f"Starting import for {employer_name}...")

        confirmation = self._show_import_confirmation()
        if not confirmation:
            self._set_processing_enabled(True)
            return

        applicable_month = f"{self.month_combo.currentText()} {self.year_combo.currentText()}".strip()
        self.worker = PayrollWorker(
            self.selected_files,
            controller=self.controller,
            applicable_month=applicable_month,
            import_data=confirmation.get("import_data", True),
            generate_sheets=confirmation.get("generate_sheets", []),
        )
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.confirm_overwrite.connect(self.handle_duplicate_confirmation)
        self.worker.start()

    def update_progress(self, percent, filename):
        self.progress_bar.setValue(percent)
        self.progress_percent_label.setText(f"{max(0, min(100, int(percent)))}%")
        self.status_label.setText(f"Processing: {filename}")

    def handle_duplicate_confirmation(self, payload):
        plan = payload.get("plan")
        exact_duplicate = bool(payload.get("exact_duplicate", False))
        if exact_duplicate:
            GlassDialog(
                self,
                "Duplicate Workbook",
                "This exact workbook has already been imported.",
            ).exec()
            self.worker.overwrite_decision = False
            self.worker.overwrite_event.set()
            return

        employer = plan.employer_id or "Unknown Employer"
        client = plan.client_name or plan.client_id or "Unknown Client"
        message = (
            f"Payroll Already Exists\n\n"
            f"Employer: {employer}\n"
            f"Client: {client}\n"
            f"Applicable Month: {plan.applicable_month}\n"
            f"Payroll Period: {plan.from_date} - {plan.to_date}\n\n"
            "Do you want to overwrite this payroll?"
        )
        dialog = GlassDialog(
            self,
            "Payroll Already Exists",
            message,
            buttons=[
                ("Overwrite", lambda: self._close_duplicate_prompt(dialog, True), True),
                ("Cancel", lambda: self._close_duplicate_prompt(dialog, False), False),
            ],
        )
        dialog.exec()

    def _close_duplicate_prompt(self, dialog, decision):
        self._set_overwrite_decision(decision)
        dialog.accept()

    def _set_overwrite_decision(self, decision):
        if self.worker is not None:
            self.worker.overwrite_decision = decision
            self.worker.overwrite_event.set()

    def on_finished(self, success, message, total_hdmf=0):
        self._set_processing_enabled(True)
        self.status_label.setText("Finished." if success else "Finished with errors.")
        self.progress_percent_label.setText("100%" if success else self.progress_percent_label.text())
        if success and total_hdmf > 0 and self.dashboard_service is not None:
            month, year = get_default_month_and_year()
            self.dashboard_service.record_upload(
                "hdmf",
                total_hdmf,
                month,
                year,
                account_username=self.current_username,
            )
        self._save_state()
        GlassDialog(self, "Processing Summary", message).exec()

    def _state_path(self):
        return account_state_path(self.current_username, "earnings_panel_state.json")

    def _load_state(self):
        data = load_json_dict(self._state_path(), default={})
        files = data.get("selected_files", [])
        if isinstance(files, list):
            self.selected_files = [str(item) for item in files if str(item).strip()]
            self.list_widget.clear()
            for file_path in self.selected_files:
                self.list_widget.addItem(os.path.basename(file_path))
        self.status_label.setText(data.get("status", f"{len(self.selected_files)} file(s) ready"))

    def _save_state(self):
        save_json_dict(
            self._state_path(),
            {
                "selected_files": self.selected_files,
                "status": self.status_label.text(),
            },
        )

    def _set_processing_enabled(self, enabled):
        self.btn_add_file.setEnabled(enabled)
        self.btn_add_folder.setEnabled(enabled)
        self.btn_remove.setEnabled(enabled)
        self.btn_start.setEnabled(enabled)
