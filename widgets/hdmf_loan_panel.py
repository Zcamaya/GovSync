import os

from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from constants.styles import AppStyles
from utils.hdmf_loan_engine import separate_hdmf_loans
from widgets.glass_dialog import GlassDialog


class HDMFLoanWorker(QThread):
    finished = Signal(bool, str)

    def __init__(self, earnings_file, monitoring_file):
        super().__init__()
        self.earnings_file = earnings_file
        self.monitoring_file = monitoring_file

    def run(self):
        try:
            updates_sl, updates_cl = separate_hdmf_loans(
                self.earnings_file,
                self.monitoring_file,
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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.earnings_file_path = ""
        self.monitoring_file_path = ""
        self.worker = None
        self._setup_ui()

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
        form_holder.setStyleSheet("""
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
            QLineEdit {
                background: rgba(2, 6, 23, 0.56);
                border: 1px solid rgba(148, 163, 184, 0.24);
                border-radius: 7px;
                color: #e5e7eb;
                min-height: 34px;
                padding: 0 10px;
                font: 12px 'Segoe UI';
            }
            QLineEdit:focus {
                border-color: rgba(20, 184, 166, 0.72);
            }
        """)
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

    def start_processing(self):
        earnings_file = self.earnings_file_path or self.earnings_file.text().strip()
        monitoring_file = self.monitoring_file_path or self.monitoring_file.text().strip()
        if not earnings_file or not monitoring_file:
            GlassDialog(self, "Notice", "Please select both files.").exec()
            return

        self.btn_process.setEnabled(False)
        self.status_label.setText("Separating loans...")

        self.worker = HDMFLoanWorker(earnings_file, monitoring_file)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, success, message):
        self.btn_process.setEnabled(True)
        self.status_label.setText("Finished." if success else "Finished with errors.")
        GlassDialog(
            self,
            "HDMF Loan Summary" if success else "HDMF Loan Error",
            message,
        ).exec()
