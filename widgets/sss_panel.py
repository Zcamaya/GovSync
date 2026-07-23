import os

from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QFont, QIntValidator
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from constants.styles import AppStyles
from widgets.shared_table import RoundedTableCard, SharedTable
from services.auth_manager import get_active_account
from controllers.sss_controller import SSSController
from shared.helpers.account_state import account_state_path, resolve_account_username
from services.auth_manager import account_json_path  # compatibility alias for tests
from shared.helpers.json_state import load_json_dict, save_json_dict
from services.sss_service import (
    SSSService,
    TXT_COLUMNS,
    format_employer_id,
    get_default_month_and_year,
    get_months_list,
    get_years_list,
)
from widgets.glass_dialog import GlassDialog


class SSSBulkWorker(QThread):
    progress = Signal(int, str)
    finished = Signal(bool, str, int)

    def __init__(self, payloads, controller=None):
        super().__init__()
        self.payloads = payloads
        self.controller = controller

    def run(self):
        total = max(len(self.payloads), 1)
        results = []
        errors = []
        total_written = 0

        for index, payload in enumerate(self.payloads, start=1):
            source_path = payload["source_file_path"]
            filename = os.path.basename(source_path)
            self.progress.emit(int((index / total) * 100), filename)
            try:
                output_path, written_rows = self.controller.generate_txt(**payload)
                total_written += written_rows
                results.append(f"{filename}: {written_rows} row(s) -> {output_path}")
            except Exception as exc:
                errors.append(f"{filename}: {exc}")

        if errors:
            self.finished.emit(False, "Errors occurred:\n" + "\n".join(errors), total_written)
        else:
            self.finished.emit(True, "Processed files:\n" + "\n".join(results), total_written)


class SSSWorker(QThread):
    progress = Signal(int)
    finished = Signal(bool, str, str)

    def __init__(self, payload, controller=None):
        super().__init__()
        self.payload = payload
        self.controller = controller

    def run(self):
        try:
            output_path, written_rows = self.controller.generate_txt(
                progress_callback=self.progress.emit,
                **self.payload,
            )
            self.finished.emit(
                True,
                f"Generated {written_rows} row(s).\n\nSaved to:\n{output_path}",
                output_path,
            )
        except Exception as exc:
            self.finished.emit(False, str(exc), "")


class SSSPanel(QWidget):
    def __init__(self, parent=None, controller=None, dashboard_service=None):
        super().__init__(parent)
        self.controller = controller or SSSController()
        self.dashboard_service = dashboard_service
        self.current_username = resolve_account_username(get_active_account() or {})
        self._persist_enabled = False
        self.source_file_path = ""
        self.correction_file_path = ""
        self.txt_file_path = ""
        # Holds the full set of loaded TXT rows (unfiltered)
        self.current_txt_rows = []
        # Holds the currently displayed (filtered) rows
        self.filtered_rows = []
        # Internal flag to suppress itemChanged handling during programmatic updates
        self._suppress_table_signals = False
        self.selected_source_files = []
        self.bulk_worker = None
        self.worker = None
        self.account_info = {}
        self._setup_ui()
        self._load_state()
        self._persist_enabled = True

    def _setup_ui(self):
        self.setStyleSheet("background: transparent;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(AppStyles.PANEL_SPACING)

        title = QLabel("SSS TXT Automation")
        title.setFont(QFont("Segoe UI", 17, QFont.Bold))
        title.setStyleSheet(AppStyles.PANEL_TITLE)
        main_layout.addWidget(title)

        self.account_banner = QLabel("Linked SSS Number: Not connected")
        self.account_banner.setStyleSheet(
            "color: #94a3b8; font: 600 11px 'Segoe UI'; border: none; background: transparent;"
        )
        self.account_banner.setVisible(False)
        main_layout.addWidget(self.account_banner)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(AppStyles.UNIFIED_TAB_STYLE)

        generate_tab = QWidget()
        generate_tab.setStyleSheet("background: transparent; border: none;")
        generate_layout = QVBoxLayout(generate_tab)
        generate_layout.setContentsMargins(AppStyles.SECTION_PADDING, AppStyles.SECTION_PADDING, AppStyles.SECTION_PADDING, AppStyles.SECTION_PADDING)
        generate_layout.setSpacing(AppStyles.PANEL_SPACING)

        viewer_tab = QWidget()
        viewer_tab.setStyleSheet("background: transparent; border: none;")
        viewer_layout = QVBoxLayout(viewer_tab)
        viewer_layout.setContentsMargins(AppStyles.SECTION_PADDING, AppStyles.SECTION_PADDING, AppStyles.SECTION_PADDING, AppStyles.SECTION_PADDING)
        viewer_layout.setSpacing(AppStyles.INNER_PADDING)

        self.tabs.addTab(generate_tab, "Generate TXT")
        self.tabs.addTab(viewer_tab, "TXT Viewer")
        main_layout.addWidget(self.tabs, stretch=1)

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
            QComboBox::drop-down {
                border: none;
                width: 28px;
            }
            QComboBox QAbstractItemView {
                background: #0f201c;
                border: 1px solid rgba(148, 163, 184, 0.42);
                border-radius: 6px;
                color: #e5e7eb;
                selection-background-color: #145f52;
                selection-color: #ffffff;
                outline: none;
                padding: 4px;
            }
            QComboBox QAbstractItemView::item {
                min-height: 28px;
                padding: 6px 10px;
            }
            """
            + AppStyles.FIELD_INPUT
            + AppStyles.SCROLLBAR
        )
        form_layout = QFormLayout(form_holder)
        form_layout.setContentsMargins(22, 22, 22, 22)
        form_layout.setSpacing(14)
        form_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        form_layout.setFormAlignment(Qt.AlignTop)
        form_layout.setHorizontalSpacing(18)

        self.employer_id = QLineEdit()
        self.employer_id.setText(format_employer_id("0391148192"))
        self.employer_id.textEdited.connect(self._format_employer_id)
        self.employer_id.textChanged.connect(self._save_state)
        form_layout.addRow("Employer SSS ID", self.employer_id)

        self.branch_code = QLineEdit("000")
        self.branch_code.setValidator(QIntValidator(0, 999, self))
        self.branch_code.setMaxLength(3)
        self.branch_code.textChanged.connect(self._save_state)
        form_layout.addRow("Branch Code", self.branch_code)

        period_row = QWidget()
        period_row.setStyleSheet("border: none; background: transparent;")
        period_layout = QHBoxLayout(period_row)
        period_layout.setContentsMargins(0, 0, 0, 0)
        period_layout.setSpacing(10)

        self.month_combo = QComboBox()
        self.month_combo.addItems(get_months_list())
        self.month_combo.setStyleSheet(AppStyles.GLOBAL_DROPDOWN)
        self.year_combo = QComboBox()
        self.year_combo.addItems(get_years_list())
        self.year_combo.setStyleSheet(AppStyles.GLOBAL_DROPDOWN)
        self.month_combo.currentTextChanged.connect(self._save_state)
        self.year_combo.currentTextChanged.connect(self._save_state)

        default_month, default_year = get_default_month_and_year()
        self.month_combo.setCurrentText(default_month)
        self.year_combo.setCurrentText(default_year)

        period_layout.addWidget(self.month_combo, stretch=2)
        period_layout.addWidget(self.year_combo, stretch=1)
        form_layout.addRow("Applicable Period", period_row)

        self.output_folder = self._path_row(
            form_layout,
            "Save Folder",
            "Select output folder",
            self.browse_output_folder,
        )
        self.output_folder.textChanged.connect(self._save_state)
        self.correction_file = self._path_row(
            form_layout,
            "Correction Excel",
            "Optional correction file",
            self.browse_correction_file,
        )
        self.correction_file.textChanged.connect(self._save_state)

        generate_layout.addWidget(form_holder)

        queue_header = QHBoxLayout()
        queue_header.setSpacing(8)
        queue_label = QLabel("Bulk Source Queue")
        queue_label.setStyleSheet(AppStyles.SECTION_TITLE)
        queue_header.addWidget(queue_label)
        queue_header.addStretch()
        self.btn_add_sources = self._secondary_button("Add Files")
        self.btn_add_sources.clicked.connect(self.add_source_files)
        self.btn_add_folder = self._secondary_button("Add Folder")
        self.btn_add_folder.clicked.connect(self.add_source_folder)
        self.btn_clear_sources = self._secondary_button("Clear Queue")
        self.btn_clear_sources.clicked.connect(self.clear_source_queue)
        queue_header.addWidget(self.btn_add_sources)
        queue_header.addWidget(self.btn_add_folder)
        queue_header.addWidget(self.btn_clear_sources)
        generate_layout.addLayout(queue_header)

        self.source_queue = QListWidget()
        self.source_queue.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.source_queue.setStyleSheet("""
            QListWidget {
                background: rgba(2, 6, 23, 0.46);
                border: 1px solid rgba(148, 163, 184, 0.22);
                border-radius: 12px;
                color: #dbeafe;
                font: 12px 'Segoe UI';
                padding: 10px 8px;
                outline: none;
            }
            QListWidget::viewport {
                border-radius: 12px;
                background: transparent;
            }
            QListWidget::item {
                padding: 8px 12px;
                margin: 2px 4px;
                border-radius: 10px;
            }
            QListWidget::item:selected {
                background: rgba(20, 184, 166, 0.22);
                color: #ecfeff;
            }
        """)
        generate_layout.addWidget(self.source_queue)

        self.btn_generate = QPushButton("Generate Partial List TXT File")
        self.btn_generate.setCursor(Qt.PointingHandCursor)
        self.btn_generate.setMinimumHeight(50)
        self.btn_generate.setStyleSheet(AppStyles.PRIMARY_BUTTON)
        self.btn_generate.clicked.connect(self.start_generation)
        generate_layout.addWidget(self.btn_generate)
        generate_layout.addStretch()

        viewer_header = QHBoxLayout()
        viewer_header.setSpacing(8)

        viewer_title = QLabel("Partial List TXT Viewer")
        viewer_title.setStyleSheet(AppStyles.SECTION_TITLE)
        viewer_header.addWidget(viewer_title, stretch=1)

        self.btn_import_txt = self._secondary_button("Import TXT")
        self.btn_import_txt.clicked.connect(self.import_txt_file)
        self.btn_save_txt = self._secondary_button("Save TXT")
        self.btn_save_txt.clicked.connect(self.save_txt_file)

        viewer_header.addWidget(self.btn_import_txt)
        viewer_header.addWidget(self.btn_save_txt)
        # Search bar for filtering loaded TXT rows
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search TXT rows...")
        self.search_input.setMinimumHeight(34)
        self.search_input.textChanged.connect(self._apply_search_filter)
        viewer_header.addWidget(self.search_input)

        # Delete currently selected row(s)
        self.btn_delete_row = self._secondary_button("Delete Row")
        self.btn_delete_row.clicked.connect(self.delete_selected_row)
        viewer_header.addWidget(self.btn_delete_row)
        viewer_layout.addLayout(viewer_header)

        self.txt_table = RoundedTableCard(TXT_COLUMNS, self)
        self.txt_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.txt_table.horizontalHeader().setStretchLastSection(True)
        self.txt_table.setAlternatingRowColors(False)
        self.txt_table.set_row_height(36)
        self.txt_table.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.txt_table.setStyleSheet(AppStyles.TABLE_CANONICAL)
        viewer_layout.addWidget(self.txt_table, stretch=1)
        # Keep table edits in sync with `current_txt_rows`
        self.txt_table.itemChanged.connect(self._on_table_item_changed)

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
        self._refresh_account_banner()

    def _secondary_button(self, text):
        button = QPushButton(text)
        button.setCursor(Qt.PointingHandCursor)
        button.setMinimumHeight(34)
        button.setMinimumWidth(82)
        button.setStyleSheet(AppStyles.SECONDARY_BUTTON)
        return button

    def set_account(self, account):
        if isinstance(account, dict):
            self.account_info = account
        else:
            self.account_info = {"username": str(account or "")}
        self.current_username = self.account_info.get("username") or "default"
        self._reset_ui_state()
        self._refresh_account_banner()
        self._load_state()

    def _reset_ui_state(self):
        self.progress_bar.setValue(0)
        self.status_label.setText("Ready")

    def _refresh_account_banner(self):
        sss_number = str(self.account_info.get("sss_number", "")).strip()
        if sss_number:
            self.employer_id.setText(format_employer_id(sss_number))
            self.account_banner.setText(f"Linked SSS Number: {format_employer_id(sss_number)}")
            self.account_banner.setVisible(True)
        else:
            self.account_banner.setText("Linked SSS Number: Not connected")
            self.account_banner.setVisible(False)

    def _state_path(self):
        return account_state_path(self.current_username, "sss_panel_state.json")

    def _load_state(self):
        # Clear form fields first to avoid stale data from previous account
        self.source_queue.clear()
        self.selected_source_files = []
        self.output_folder.clear()
        self.correction_file.clear()
        self.correction_file_path = ""
        self.txt_file_path = ""
        data = load_json_dict(self._state_path(), default={})

        self.selected_source_files = [str(item) for item in data.get("selected_source_files", []) if str(item).strip()]
        self.source_queue.clear()
        for file_path in self.selected_source_files:
            self.source_queue.addItem(os.path.basename(file_path))

        output_folder = str(data.get("output_folder", "")).strip()
        if output_folder:
            self.output_folder.setText(output_folder)

        self.correction_file_path = str(data.get("correction_file_path", "")).strip()
        if self.correction_file_path:
            self.correction_file.setText(os.path.basename(self.correction_file_path))

        employer_id = str(data.get("employer_id", "")).strip()
        if employer_id:
            self.employer_id.setText(employer_id)

        branch_code = str(data.get("branch_code", "")).strip()
        if branch_code:
            self.branch_code.setText(branch_code)

        month = str(data.get("month", "")).strip()
        year = str(data.get("year", "")).strip()
        if month:
            self.month_combo.setCurrentText(month)
        if year:
            self.year_combo.setCurrentText(year)

        self.txt_file_path = str(data.get("txt_file_path", "")).strip()
        self.status_label.setText(str(data.get("status", self.status_label.text())).strip())

    def _save_state(self):
        if not getattr(self, "_persist_enabled", False):
            return
        save_json_dict(
            self._state_path(),
            {
            "selected_source_files": self.selected_source_files,
            "output_folder": self.output_folder.text().strip(),
            "correction_file_path": self.correction_file_path,
            "employer_id": self.employer_id.text().strip(),
            "branch_code": self.branch_code.text().strip(),
            "month": self.month_combo.currentText(),
            "year": self.year_combo.currentText(),
            "txt_file_path": self.txt_file_path,
            "status": self.status_label.text(),
            },
        )

    def _path_row(self, form_layout, label, placeholder, browse_callback):
        row = QWidget()
        row.setStyleSheet("border: none; background: transparent;")
        row.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(8)

        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        line_edit.setMinimumHeight(34)

        button = QPushButton("Browse")
        button.setCursor(Qt.PointingHandCursor)
        button.setFixedSize(86, 34)
        button.setStyleSheet(AppStyles.SECONDARY_BUTTON)
        button.clicked.connect(browse_callback)

        row_layout.addWidget(line_edit)
        row_layout.addWidget(button)
        form_layout.addRow(label, row)
        return line_edit

    def _format_employer_id(self, value):
        formatted = format_employer_id(value)
        if formatted == value:
            return

        self.employer_id.blockSignals(True)
        self.employer_id.setText(formatted)
        self.employer_id.blockSignals(False)

    def browse_source_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Source Excel File",
            "",
            "Excel Files (*.xlsx *.xlsm)",
        )
        if path:
            self.source_file_path = path

    def browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Save Folder")
        if folder:
            self.output_folder.setText(folder)
            self._save_state()

    def browse_correction_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Correction Excel File",
            "",
            "Excel Files (*.xlsx *.xlsm)",
        )
        if path:
            self.correction_file_path = path
            self.correction_file.setText(os.path.basename(path))
            self._save_state()

    def add_source_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select SSS Source Excel Files",
            "",
            "Excel Files (*.xlsx *.xlsm)",
        )
        self._add_source_paths(files)

    def add_source_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select SSS Source Folder")
        if not folder:
            return

        files = [
            os.path.join(folder, filename)
            for filename in sorted(os.listdir(folder))
            if filename.lower().endswith((".xlsx", ".xlsm"))
        ]
        self._add_source_paths(files)

    def clear_source_queue(self):
        self.selected_source_files = []
        self.source_queue.clear()
        self.status_label.setText("Queue cleared.")
        self._save_state()

    def _add_source_paths(self, paths):
        for path in paths:
            if path and path not in self.selected_source_files:
                self.selected_source_files.append(path)
                self.source_queue.addItem(os.path.basename(path))
        self.status_label.setText(f"{len(self.selected_source_files)} file(s) queued.")
        self._save_state()

    def import_txt_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Partial List TXT",
            "",
            "Text Files (*.txt);;All Files (*.*)",
        )
        if not path:
            return

        try:
            rows = self.controller.load_txt(path)
        except Exception as exc:
            GlassDialog(self, "TXT Import Error", str(exc)).exec()
            return

        # Store full rows and render
        self.current_txt_rows = rows
        self.filtered_rows = list(rows)
        self.txt_file_path = path
        self._render_txt_table(self.filtered_rows)
        self.status_label.setText(f"Loaded {len(rows)} TXT row(s).")
        self._save_state()

    def save_txt_file(self):
        if self.txt_table.rowCount() == 0:
            GlassDialog(self, "Notice", "Import a TXT file first.").exec()
            return

        path = self.txt_file_path
        if not path:
            path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Partial List TXT",
                "",
                "Text Files (*.txt)",
            )
            if not path:
                return

        # Save from the underlying data model (not just visible rows)
        rows = list(self.current_txt_rows)
        try:
            output_path, written_rows = self.controller.save_txt(rows, path)
        except Exception as exc:
            GlassDialog(self, "TXT Save Error", str(exc)).exec()
            return

        self.txt_file_path = output_path
        self.status_label.setText(f"Saved {written_rows} TXT row(s).")
        self._save_state()
        GlassDialog(self, "TXT Saved", f"Saved {written_rows} row(s).\n\n{output_path}").exec()

    def _populate_txt_table(self, rows):
        # Deprecated: use _render_txt_table for direct rendering.
        self.current_txt_rows = rows
        self.filtered_rows = list(rows)
        self._render_txt_table(rows)

    def _render_txt_table(self, rows):
        # Render rows into the table while avoiding firing itemChanged
        self._suppress_table_signals = True
        try:
            self.txt_table.setRowCount(len(rows))

            for row_index, row in enumerate(rows):
                for column_index, column_name in enumerate(TXT_COLUMNS):
                    item = QTableWidgetItem(str(row.get(column_name, "")))
                    self.txt_table.setItem(row_index, column_index, item)
        finally:
            self._suppress_table_signals = False

        # Clear selection after rendering
        self.txt_table.clearSelection()

    def _on_table_item_changed(self, item: QTableWidgetItem):
        if getattr(self, "_suppress_table_signals", False):
            return

        row_idx = item.row()
        col_idx = item.column()
        if not (0 <= row_idx < len(self.filtered_rows)):
            return

        column_name = TXT_COLUMNS[col_idx]
        new_value = item.text().strip() if item.text().strip() else "NULL"

        # Update the visible (filtered) row object — this mutates the same dict in current_txt_rows
        try:
            self.filtered_rows[row_idx][column_name] = new_value
        except Exception:
            return

        # No further action needed because filtered_rows references current_txt_rows entries
        # Update UI status
        self.status_label.setText("Edited row saved to memory.")
        self._save_state()

    def _apply_search_filter(self):
        query = self.search_input.text().strip().lower()
        if not query:
            self.filtered_rows = list(self.current_txt_rows)
        else:
            matched = []
            for row in self.current_txt_rows:
                for val in row.values():
                    if query in (str(val) or "").lower():
                        matched.append(row)
                        break
            self.filtered_rows = matched
        self._render_txt_table(self.filtered_rows)

    def delete_selected_row(self):
        selected_ranges = self.txt_table.selectedRanges()
        if not selected_ranges:
            GlassDialog(self, "Notice", "Select a row to delete.").exec()
            return

        # Collect selected row indexes (visible indexes)
        rows_to_delete = set()
        for sel in selected_ranges:
            for r in range(sel.topRow(), sel.bottomRow() + 1):
                rows_to_delete.add(r)

        # Map visible indexes to underlying rows in filtered_rows
        to_remove = []
        for idx in sorted(rows_to_delete, reverse=True):
            if 0 <= idx < len(self.filtered_rows):
                to_remove.append(self.filtered_rows[idx])

        # Remove from full rows list
        for row in to_remove:
            try:
                self.current_txt_rows.remove(row)
            except ValueError:
                # fallback: remove by matching values
                for existing in list(self.current_txt_rows):
                    if all(str(existing.get(k, "")) == str(row.get(k, "")) for k in TXT_COLUMNS):
                        self.current_txt_rows.remove(existing)
                        break

        # Reapply current filter to refresh view
        self._apply_search_filter()
        self.status_label.setText(f"Deleted {len(to_remove)} row(s).")
        self._save_state()

    def _table_rows(self):
        rows = []
        for row_index in range(self.txt_table.rowCount()):
            row = {}
            for column_index, column_name in enumerate(TXT_COLUMNS):
                item = self.txt_table.item(row_index, column_index)
                row[column_name] = item.text().strip() if item else "NULL"
            rows.append(row)
        return rows

    def start_generation(self):
        output_directory = self.output_folder.text().strip()
        if not output_directory:
            GlassDialog(self, "Notice", "Please select a save folder.").exec()
            return

        source_files = list(self.selected_source_files)
        if not source_files:
            GlassDialog(self, "Notice", "Please select at least one source file.").exec()
            return

        payloads = []
        for source_file_path in source_files:
            payloads.append(
                {
                    "source_file_path": source_file_path,
                    "output_directory": output_directory,
                    "correction_file_path": self.correction_file_path
                    or self.correction_file.text().strip(),
                    "employer_id": self.employer_id.text().strip(),
                    "branch_code": self.branch_code.text().strip(),
                    "month": self.month_combo.currentText(),
                    "year": self.year_combo.currentText(),
                }
            )

        self._set_enabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Generating TXT file(s)...")
        self._save_state()

        if len(payloads) == 1:
            self.worker = SSSWorker(payloads[0], controller=self.controller)
            self.worker.progress.connect(self.progress_bar.setValue)
            self.worker.finished.connect(self.on_finished)
            self.worker.start()
            return

        self.bulk_worker = SSSBulkWorker(payloads, controller=self.controller)
        self.bulk_worker.progress.connect(self._on_bulk_progress)
        self.bulk_worker.finished.connect(self._on_bulk_finished)
        self.bulk_worker.start()

    def _on_bulk_progress(self, percent, filename):
        self.progress_bar.setValue(percent)
        self.progress_percent_label.setText(f"{max(0, min(100, int(percent)))}%")
        self.status_label.setText(f"Processing: {filename}")

    def _on_bulk_finished(self, success, message, total_rows=0):
        self._set_enabled(True)
        self.status_label.setText("Finished." if success else "Finished with errors.")
        self.progress_percent_label.setText("100%" if success else self.progress_percent_label.text())
        if success and total_rows > 0 and self.dashboard_service is not None:
            self.dashboard_service.record_upload(
                "sss",
                total_rows,
                self.month_combo.currentText(),
                self.year_combo.currentText(),
                account_username=self.current_username,
            )
        GlassDialog(
            self,
            "SSS Bulk Processing Summary" if success else "SSS Bulk Processing Error",
            message,
        ).exec()

    def on_finished(self, success, message, output_path):
        self._set_enabled(True)
        self.status_label.setText("Finished." if success else "Finished with errors.")
        self.progress_percent_label.setText("100%" if success else self.progress_percent_label.text())

        if success and output_path:
            try:
                rows = self.controller.load_txt(output_path)
                self.txt_file_path = output_path
                self._populate_txt_table(rows)
                self.tabs.setCurrentIndex(1)
                self.status_label.setText(f"Generated and loaded {len(rows)} TXT row(s).")
                if self.dashboard_service is not None:
                    self.dashboard_service.record_upload(
                        "sss",
                        len(rows),
                        self.month_combo.currentText(),
                        self.year_combo.currentText(),
                        account_username=self.current_username,
                    )
                self._save_state()
            except Exception as exc:
                message = f"{message}\n\nViewer load failed: {exc}"

        GlassDialog(
            self,
            "SSS Processing Summary" if success else "SSS Processing Error",
            message,
        ).exec()

    def _set_enabled(self, enabled):
        self.btn_generate.setEnabled(enabled)
        self.btn_import_txt.setEnabled(enabled)
        self.btn_save_txt.setEnabled(enabled)
        self.btn_add_sources.setEnabled(enabled)
        self.btn_add_folder.setEnabled(enabled)
        self.btn_clear_sources.setEnabled(enabled)
