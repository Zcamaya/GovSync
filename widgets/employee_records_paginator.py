from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
)


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
        button_style = """
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
        self.prev_button.setStyleSheet(button_style)
        self.next_button.setStyleSheet(button_style)

        self.page_label = QLabel("Page 1")
        self.page_label.setStyleSheet("color: #cbd5e1;")

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
