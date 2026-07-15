import calendar as cal_lib
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class CustomReferenceCalendar(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("CustomReferenceCalendar")
        self.setStyleSheet("""
            QFrame#CustomReferenceCalendar {
                background: rgba(15, 23, 42, 0.82);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 20px;
            }
            QLabel { color: #f8fafc; background: transparent; }
            QPushButton {
                background: rgba(15, 23, 42, 0.0);
                color: #94a3b8;
                border: 1px solid rgba(148, 163, 184, 0.22);
                border-radius: 10px;
                font: 700 11px 'Segoe UI';
                min-width: 24px;
                min-height: 24px;
            }
            QPushButton:hover { color: #ffffff; border-color: rgba(56, 189, 248, 0.45); }
        """)

        self.now = datetime.now()
        self.current_year = self.now.year
        self.current_month = self.now.month

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        self.setFixedHeight(270)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        header_layout = QHBoxLayout()
        self.lbl_month_year = QLabel()
        self.lbl_month_year.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.lbl_month_year.setStyleSheet("color: #f8fafc;")

        btn_prev = QPushButton("<")
        btn_prev.setFixedSize(28, 28)
        btn_prev.setCursor(Qt.PointingHandCursor)
        btn_prev.clicked.connect(lambda: self.change_month(-1))

        btn_next = QPushButton(">")
        btn_next.setFixedSize(28, 28)
        btn_next.setCursor(Qt.PointingHandCursor)
        btn_next.clicked.connect(lambda: self.change_month(1))

        btn_prev.setStyleSheet("border: 1px solid rgba(148, 163, 184, 0.22); border-radius: 12px; background: rgba(15, 23, 42, 0.4);")
        btn_next.setStyleSheet("border: 1px solid rgba(148, 163, 184, 0.22); border-radius: 12px; background: rgba(15, 23, 42, 0.4);")

        header_layout.addWidget(btn_prev)
        header_layout.addWidget(self.lbl_month_year, alignment=Qt.AlignCenter)
        header_layout.addWidget(btn_next)

        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(5)

        layout.addLayout(header_layout)
        layout.addWidget(self.grid_container)
        self.rebuild_calendar()

    def change_month(self, delta):
        self.current_month += delta

        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        elif self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1

        self.rebuild_calendar()

    def rebuild_calendar(self):
        for index in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(index).widget()
            if widget is not None:
                widget.setParent(None)

        month_label = datetime(self.current_year, self.current_month, 1).strftime("%B %Y")
        self.lbl_month_year.setText(month_label)

        for column, day_name in enumerate(["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]):
            label = QLabel(day_name)
            label.setFont(QFont("Segoe UI", 8, QFont.Bold))
            label.setStyleSheet("color: #64748b;")
            label.setAlignment(Qt.AlignCenter)
            self.grid_layout.addWidget(label, 0, column)

        month_matrix = cal_lib.monthcalendar(self.current_year, self.current_month)
        for row_index, week in enumerate(month_matrix, start=1):
            for column_index, day in enumerate(week):
                if day == 0:
                    continue

                label = QLabel(str(day))
                label.setAlignment(Qt.AlignCenter)
                label.setFixedSize(28, 28)

                is_today = (
                    day == self.now.day
                    and self.current_month == self.now.month
                    and self.current_year == self.now.year
                )
                if is_today:
                    label.setStyleSheet(
                        "background-color: #f43f5e; border-radius: 12px; "
                        "color: white; font-weight: bold;"
                    )
                else:
                    label.setStyleSheet("color: #e2e8f0;")

                self.grid_layout.addWidget(label, row_index, column_index)
