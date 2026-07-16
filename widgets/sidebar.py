import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QImage, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QHBoxLayout, QLabel, QListWidget, QPushButton, QVBoxLayout, QWidget

from constants.styles import AppStyles
from shared.resources import asset_path


class SidebarWidget(QWidget):
    logout_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(240)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 15, 10, 15)
        layout.setSpacing(10)
        layout.addLayout(self._create_header())

        self.list_widget = self._create_nav_list()
        layout.addWidget(self.list_widget, stretch=1)
        layout.addWidget(self._create_logout_button())

    def _create_header(self):
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 10)

        logo_path = asset_path("logo.svg")

        logo_label = QLabel()
        logo_label.setFixedSize(35, 35)

        if os.path.exists(logo_path):
            renderer = QSvgRenderer(logo_path)
            image = QImage(35, 35, QImage.Format_ARGB32)
            image.fill(Qt.transparent)

            painter = QPainter(image)
            renderer.render(painter)
            painter.end()

            logo_label.setPixmap(QPixmap.fromImage(image))

        title_label = QLabel("GovSync")
        title_label.setStyleSheet(AppStyles.SCREEN_TITLE)

        header.addWidget(logo_label)
        header.addWidget(title_label)
        header.addStretch()
        return header

    def _create_nav_list(self):
        nav = QListWidget()
        nav.addItems(
            [
                "Dashboard",
                "Earnings",
                "Employee Records",
                "Philhealth",
                "HDMF",
                "SSS",
                "HDMF Loan",
            ]
        )
        nav.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        nav.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        nav.setStyleSheet(AppStyles.NAV_LIST)
        nav.setCurrentRow(0)
        nav.setAlternatingRowColors(False)
        return nav

    def _create_logout_button(self):
        button = QPushButton("Log Out")
        button.setCursor(Qt.PointingHandCursor)
        button.setMinimumHeight(42)
        button.clicked.connect(self.logout_requested.emit)
        button.setStyleSheet(AppStyles.SECONDARY_BUTTON + """
            QPushButton {
                min-height: 42px;
            }
            QPushButton:hover {
                background: rgba(244, 63, 94, 0.20);
                border-color: rgba(244, 63, 94, 0.52);
                color: #fecdd3;
            }
        """)
        return button
