from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QSizePolicy,
)

from constants.styles import AppStyles


class EmployeeRecordsTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(0, 3, parent)
        self._build_ui()
        self._current_employee_rows = []

    def _build_ui(self):
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setShowGrid(False)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.setStyleSheet(
            AppStyles.TABLE_BASE
            + AppStyles.TABLE_SCROLLBAR
            + """
            QHeaderView::section {
                background: rgba(15, 23, 42, 0.92);
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
        self.setHorizontalHeaderLabels(["No.", "Client", "Employee Name"])
        self.horizontalHeader().setStretchLastSection(False)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.setWordWrap(True)
        self.setColumnWidth(0, 48)
        self.setSortingEnabled(False)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(200)
        self.verticalHeader().setDefaultSectionSize(36)

    def populate(self, employees, search_text="", page=1, page_size=100):
        self.setRowCount(0)
        self._current_employee_rows = employees or []
        search_text = search_text.strip().lower()

        if not employees:
            self.setRowCount(1)
            empty_item = QTableWidgetItem("No records found")
            empty_item.setTextAlignment(Qt.AlignCenter)
            self.setItem(0, 0, empty_item)
            self.setSpan(0, 0, 1, self.columnCount())
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
            self.setRowHeight(row_index, 38)

    def get_current_employee(self, row):
        if 0 <= row < len(self._current_employee_rows):
            return self._current_employee_rows[row]
        return None
