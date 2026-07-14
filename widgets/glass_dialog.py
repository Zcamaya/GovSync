from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from constants.styles import AppStyles


class GlassDialog(QDialog):
    def __init__(self, parent, title, message, buttons=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(560, 380)
        self.drag_pos = QPoint()
        self._is_dragging = False

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(1, 1, 1, 1)
        outer_layout.setSpacing(0)

        self.card = QFrame()
        self.card.setObjectName("DialogCard")
        outer_layout.addWidget(self.card)

        self.setStyleSheet(AppStyles.DIALOG_BASE + """
            QLabel#DialogTitle {
                padding: 20px 24px 8px 24px;
            }
            QTextEdit {
                background: transparent;
                border: none;
                font: 13px 'Segoe UI';
                padding: 0 24px 18px 24px;
            }
        """)

        layout = QVBoxLayout(self.card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title_label = QLabel(title)
        title_label.setObjectName("DialogTitle")
        layout.addWidget(title_label)

        self.text_area = QTextEdit()
        self.text_area.setPlainText(message)
        self.text_area.setReadOnly(True)
        self.text_area.setAcceptRichText(False)
        layout.addWidget(self.text_area, stretch=1)

        self._add_buttons(layout, buttons or [("Close", self.accept, True)])

    def _add_buttons(self, layout, buttons):
        button_bar = QFrame()
        button_bar.setObjectName("ButtonBar")
        button_layout = QHBoxLayout(button_bar)
        button_layout.setContentsMargins(18, 12, 18, 12)
        button_layout.setSpacing(12)
        button_layout.addStretch()

        for index, (text, callback, is_primary) in enumerate(buttons):
            button = QPushButton(text)
            button.setCursor(Qt.PointingHandCursor)
            button.setFixedWidth(92)
            button.setFixedHeight(40)
            if is_primary:
                button.setObjectName("PrimaryButton")
            button.clicked.connect(callback)
            button_layout.addWidget(button)

        layout.addWidget(button_bar)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_dragging = True
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._is_dragging:
            next_pos = self.pos() + event.globalPosition().toPoint() - self.drag_pos
            self.move(next_pos)
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)
