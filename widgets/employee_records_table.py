from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QHeaderView, QTableWidgetItem

from constants.styles import AppStyles
from widgets.shared_table import SharedTable


class EmployeeRecordsTable(SharedTable):
    def __init__(self, parent=None):
        super().__init__(['No.', 'Client', 'Employee Name'], parent)
        self._current_employee_rows = []

    def _build_ui(self, columns):
        super()._build_ui(columns)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.setColumnWidth(0, 48)
        # keep default min height modest; panel will manage sizing responsively
        self.setMinimumHeight(140)

    def populate(self, employees, search_text="", page=1, page_size=100):
        self.setRowCount(0)
        self._current_employee_rows = employees or []
        search_text = search_text.strip().lower()

        if not employees:
            self.set_empty_state("No records found")
            return

        self.setRowCount(len(employees))
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
                str((page - 1) * page_size + row_index + 1),
                employee.get("client", ""),
                employee_name,
            ]
            for col_idx, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if search_text and search_text in str(value).lower():
                    item.setBackground(QColor(20, 100, 90))
                if col_idx in (1, 2):
                    item.setToolTip(str(value))
                self.setItem(row_index, col_idx, item)
            self.setRowHeight(row_index, AppStyles.TABLE_ROW_HEIGHT)

    def get_current_employee(self, row):
        if 0 <= row < len(self._current_employee_rows):
            return self._current_employee_rows[row]
        return None
