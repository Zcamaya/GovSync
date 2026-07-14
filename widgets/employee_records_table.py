from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QSizePolicy,
)


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
            "QTableWidget { background: #071b1b; color: #dbeafe; border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; margin-right: 2px; }"
            " QHeaderView::section { background: #2b3744; color: #f8fafc; padding: 8px; border: none; font-weight: 700; }"
            " QTableWidget::item { padding: 6px 8px; border-bottom: 1px solid rgba(255,255,255,0.04); }"
            " QTableWidget::item:selected { background: #0f766e; color: #ffffff; }"
            " QTableWidget::item:alternate { background: #041516; }"
            " QTableWidget QScrollBar:vertical { background: rgba(15,23,42,0.48); width: 12px; border-radius: 6px; margin: 2px; }"
            " QTableWidget QScrollBar::handle:vertical { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #14b8a6, stop:1 #3b82f6); border-radius: 6px; min-height: 20px; }"
            " QTableWidget QScrollBar::handle:vertical:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2dd4bf, stop:1 #60a5fa); }",
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
