import json
import os

from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
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
from services.auth_manager import account_json_path, get_active_account
from services.dashboard_service import record_upload
from controllers.payroll_controller import PayrollController
from widgets.glass_dialog import GlassDialog


class PayrollWorker(QThread):
    progress = Signal(int, str)
    finished = Signal(bool, str, int)

    def __init__(self, files, controller=None):
        super().__init__()
        self.files = files
        self.controller = controller

    def run(self):
        total = len(self.files)
        errors = []
        total_hdmf = 0

        for index, path in enumerate(self.files, start=1):
            filename = os.path.basename(path)
            self.progress.emit(int((index / total) * 100), filename)

            try:
                success, message, hdmf_count = self.controller.process_file(
                    path,
                    progress_callback=self.progress.emit,
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
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.selected_files = []
        self.controller = controller or PayrollController()
        self.current_username = (get_active_account() or {}).get("username") or "default"
        self.worker = None
        self._setup_ui()
        self._load_state()

    def set_account(self, account):
        if isinstance(account, dict):
            username = account.get("username", "")
        else:
            username = str(account or "")
        self.current_username = username or "default"
        self._load_state()

    def _setup_ui(self):
        self.setStyleSheet("background: transparent;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(14)

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
                padding: 12px;
                outline: none;
            }
            QListWidget::item {
                border: none;
                border-radius: 6px;
                padding: 8px 10px;
                margin: 1px 0;
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

        self.btn_start = QPushButton("Start Processing")
        self.btn_start.setCursor(Qt.PointingHandCursor)
        self.btn_start.setMinimumHeight(50)
        self.btn_start.setStyleSheet(AppStyles.PRIMARY_BUTTON)
        self.btn_start.clicked.connect(self.start_processing)
        main_layout.addWidget(self.btn_start)

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
        self.status_label.setText("Starting...")

        self.worker = PayrollWorker(self.selected_files, controller=self.controller)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def update_progress(self, percent, filename):
        self.progress_bar.setValue(percent)
        self.progress_percent_label.setText(f"{max(0, min(100, int(percent)))}%")
        self.status_label.setText(f"Processing: {filename}")

    def on_finished(self, success, message, total_hdmf=0):
        self._set_processing_enabled(True)
        self.status_label.setText("Finished." if success else "Finished with errors.")
        self.progress_percent_label.setText("100%" if success else self.progress_percent_label.text())
        if success and total_hdmf > 0:
            month, year = get_default_month_and_year()
            record_upload("hdmf", total_hdmf, month, year)
        self._save_state()
        GlassDialog(self, "Processing Summary", message).exec()

    def _state_path(self):
        return account_json_path(self.current_username, "earnings_panel_state.json")

    def _load_state(self):
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
        files = data.get("selected_files", [])
        if isinstance(files, list):
            self.selected_files = [str(item) for item in files if str(item).strip()]
            self.list_widget.clear()
            for file_path in self.selected_files:
                self.list_widget.addItem(os.path.basename(file_path))
        self.status_label.setText(data.get("status", f"{len(self.selected_files)} file(s) ready"))

    def _save_state(self):
        path = self._state_path()
        data = {
            "selected_files": self.selected_files,
            "status": self.status_label.text(),
        }
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as output_file:
            json.dump(data, output_file, indent=2)

    def _set_processing_enabled(self, enabled):
        self.btn_add_file.setEnabled(enabled)
        self.btn_add_folder.setEnabled(enabled)
        self.btn_remove.setEnabled(enabled)
        self.btn_start.setEnabled(enabled)
