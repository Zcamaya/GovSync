from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
)

from constants.styles import AppStyles


class EmployeeRecordsPaginator(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        self.setMinimumHeight(52)
        self.setMaximumHeight(52)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self.prev_button = QPushButton("← Previous")
        self.next_button = QPushButton("Next →")
        self.prev_button.setStyleSheet(AppStyles.TABLE_PAGINATION_BUTTON)
        self.next_button.setStyleSheet(AppStyles.TABLE_PAGINATION_BUTTON)

        self.page_label = QLabel("Page 1")
        self.page_label.setStyleSheet(AppStyles.TABLE_METADATA_TEXT)

        layout.addStretch()
        layout.addWidget(self.prev_button)
        layout.addWidget(self.page_label)
        layout.addWidget(self.next_button)
        layout.addStretch()

    def update_page(self, page):
        self.page_label.setText(f"Page {page}")

    def set_buttons_enabled(self, prev_enabled: bool, next_enabled: bool):
        self.prev_button.setEnabled(prev_enabled)
        self.next_button.setEnabled(next_enabled)
