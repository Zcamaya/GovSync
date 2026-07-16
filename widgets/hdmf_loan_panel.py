import json
import os

from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from constants.styles import AppStyles
from services.auth_manager import account_json_path, get_active_account
from controllers.hdmf_controller import HDMFController
from widgets.glass_dialog import GlassDialog


class HDMFLoanWorker(QThread):
    progress = Signal(int, str, str)
    finished = Signal(bool, str)

    def __init__(self, earnings_file, monitoring_file, controller=None):
        super().__init__()
        self.earnings_file = earnings_file
        self.monitoring_file = monitoring_file
        self.controller = controller

    def run(self):
        try:
            updates_sl, updates_cl = self.controller.separate_loans(
                self.earnings_file,
                self.monitoring_file,
                progress_callback=self.progress.emit,
            )
            self.finished.emit(
                True,
                "File updated successfully.\n\n"
                f"SL (MPL) deductions: {updates_sl}\n"
                f"CL (CAL) deductions: {updates_cl}",
            )
        except Exception as exc:
            self.finished.emit(False, str(exc))


class HDMFLoanPanel(QWidget):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller or HDMFController()
        self.current_username = (get_active_account() or {}).get("username") or "default"
        self._persist_enabled = False
        self.earnings_file_path = ""
        self.monitoring_file_path = ""
        self.worker = None
        self._setup_ui()
        self._load_state()
        self._persist_enabled = True

    def set_account(self, account):
        if isinstance(account, dict):
            username = account.get("username", "")
        else:
            username = str(account or "")
        self.current_username = username or "default"
        self._reset_ui_state()
        self._load_state()

    def _reset_ui_state(self):
        self.progress_bar.setValue(0)
        self.status_label.setText("Ready")

    def _setup_ui(self):
        self.setStyleSheet("background: transparent;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(14)

        title = QLabel("HDMF Loan Separator")
        title.setFont(QFont("Segoe UI", 17, QFont.Bold))
        title.setStyleSheet(AppStyles.PANEL_TITLE)
        main_layout.addWidget(title)

        form_holder = QWidget()
        form_holder.setStyleSheet(
            """
            QWidget {
                background: rgba(20, 43, 37, 0.64);
                border: 1px solid rgba(148, 163, 184, 0.22);
                border-radius: 10px;
            }
            QLabel {
                color: #cbd5e1;
                border: none;
                background: transparent;
                font: 600 12px 'Segoe UI';
            }
        """
            + AppStyles.FIELD_INPUT
        )
        form_layout = QFormLayout(form_holder)
        form_layout.setContentsMargins(22, 22, 22, 22)
        form_layout.setSpacing(12)

        self.earnings_file = self._path_row(
            form_layout,
            "Earnings File",
            "Select earnings file with HDMF_LOANS sheet",
            self.browse_earnings_file,
        )
        self.monitoring_file = self._path_row(
            form_layout,
            "Monitoring File",
            "Select HDMF monitoring file",
            self.browse_monitoring_file,
        )
        main_layout.addWidget(form_holder)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(
            "color: #94a3b8; font-size: 11px; border: none; background: transparent;"
        )
        main_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
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

        self.btn_process = QPushButton("Separate Loans")
        self.btn_process.setCursor(Qt.PointingHandCursor)
        self.btn_process.setMinimumHeight(50)
        self.btn_process.setStyleSheet(AppStyles.PRIMARY_BUTTON)
        self.btn_process.clicked.connect(self.start_processing)
        main_layout.addWidget(self.btn_process)
        main_layout.addStretch()

    def _path_row(self, form_layout, label, placeholder, browse_callback):
        row = QWidget()
        row.setStyleSheet("border: none; background: transparent;")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)

        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)

        button = QPushButton("Browse")
        button.setCursor(Qt.PointingHandCursor)
        button.setFixedWidth(92)
        button.setStyleSheet(AppStyles.SECONDARY_BUTTON)
        button.clicked.connect(browse_callback)

        row_layout.addWidget(line_edit)
        row_layout.addWidget(button)
        form_layout.addRow(label, row)
        return line_edit

    def browse_earnings_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Earnings File",
            "",
            "Excel Files (*.xlsx *.xlsm)",
        )
        if path:
            self.earnings_file_path = path
            self.earnings_file.setText(os.path.basename(path))
            self._save_state()

    def browse_monitoring_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Monitoring File",
            "",
            "Excel Files (*.xlsx *.xlsm)",
        )
        if path:
            self.monitoring_file_path = path
            self.monitoring_file.setText(os.path.basename(path))
            self._save_state()

    def start_processing(self):
        earnings_file = self.earnings_file_path or self.earnings_file.text().strip()
        monitoring_file = self.monitoring_file_path or self.monitoring_file.text().strip()
        if not earnings_file or not monitoring_file:
            GlassDialog(self, "Notice", "Please select both files.").exec()
            return

        self.btn_process.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_percent_label.setText("0%")
        self.status_label.setText("Separating loans...")
        self._save_state()

        self.worker = HDMFLoanWorker(earnings_file, monitoring_file, controller=self.controller)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def _on_progress(self, percent, filename, message):
        value = max(0, min(100, int(percent)))
        self.progress_bar.setValue(value)
        self.progress_percent_label.setText(f"{value}%")
        if message:
            self.status_label.setText(message)
        elif filename:
            self.status_label.setText(f"Working on {os.path.basename(filename)}")
        else:
            self.status_label.setText("Separating loans...")

    def on_finished(self, success, message):
        self.btn_process.setEnabled(True)
        self.progress_bar.setValue(100 if success else self.progress_bar.value())
        if success:
            self.progress_percent_label.setText("100%")
        self.status_label.setText("Finished." if success else "Finished with errors.")
        self._save_state()
        GlassDialog(
            self,
            "HDMF Loan Summary" if success else "HDMF Loan Error",
            message,
        ).exec()

    def _state_path(self):
        return account_json_path(self.current_username, "hdmf_loan_panel_state.json")

    def _load_state(self):
        # Clear form fields first to avoid stale data from previous account
        self.earnings_file.clear()
        self.monitoring_file.clear()
        self.earnings_file_path = ""
        self.monitoring_file_path = ""
        
        path = self._state_path()
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as input_file:
                data = json.load(input_file)
        except (OSError, json.JSONDecodeError):
            return
        if not isinstance(data, dict):
            return

        self.earnings_file_path = str(data.get("earnings_file_path", "")).strip()
        self.monitoring_file_path = str(data.get("monitoring_file_path", "")).strip()
        if self.earnings_file_path:
            self.earnings_file.setText(os.path.basename(self.earnings_file_path))
        if self.monitoring_file_path:
            self.monitoring_file.setText(os.path.basename(self.monitoring_file_path))
        self.status_label.setText(str(data.get("status", self.status_label.text())).strip())

    def _save_state(self):
        if not getattr(self, "_persist_enabled", False):
            return
        path = self._state_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as output_file:
            json.dump(
                {
                    "earnings_file_path": self.earnings_file_path,
                    "monitoring_file_path": self.monitoring_file_path,
                    "status": self.status_label.text(),
                },
                output_file,
                indent=2,
            )
