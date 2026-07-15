from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from constants.styles import AppStyles
from widgets.glass_dialog import GlassDialog


class EmployerFormDialog(QDialog):
    def __init__(self, parent=None, employer=None):
        super().__init__(parent)
        self.employer = employer
        self.setWindowTitle("Employer" if employer is None else "Edit Employer")
        self.setModal(True)
        self.setMinimumWidth(460)
        self._build_ui()
        if employer is not None:
            self._populate(employer)

    def _build_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumWidth(560)
        self.setMinimumHeight(520)
        self.drag_pos = QPoint()
        self._is_dragging = False

        self.setStyleSheet(AppStyles.DIALOG_BASE)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(1, 1, 1, 1)
        outer_layout.setSpacing(0)

        self.card = QFrame()
        self.card.setObjectName("DialogCard")
        outer_layout.addWidget(self.card)

        layout = QVBoxLayout(self.card)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("Employer" if self.employer is None else "Edit Employer")
        title.setObjectName("DialogTitle")
        layout.addWidget(title)

        subtitle = QLabel("Manage employer details and status.")
        subtitle.setStyleSheet("color: #94a3b8; font: 600 12px 'Segoe UI';")
        layout.addWidget(subtitle)

        form = QFormLayout()
        form.setSpacing(10)

        self.name_input = QLineEdit()
        self.address_input = QLineEdit()
        self.tin_input = QLineEdit()
        self.sss_input = QLineEdit()
        self.sss_input.setInputMask("00-0000000-0;_")
        self.philhealth_input = QLineEdit()
        self.philhealth_input.setInputMask("00-000000000-0;_")
        self.hdmf_input = QLineEdit()
        self.hdmf_input.setInputMask("0000-0000-0000;_")
        self.status_combo = QComboBox()
        self.status_combo.addItems(["active", "inactive"])
        self.status_combo.setStyleSheet(AppStyles.GLOBAL_DROPDOWN)

        form.addRow("Employer Name", self.name_input)
        form.addRow("Address", self.address_input)
        form.addRow("TIN", self.tin_input)
        form.addRow("SSS Number", self.sss_input)
        form.addRow("PhilHealth Number", self.philhealth_input)
        form.addRow("HDMF Number", self.hdmf_input)
        form.addRow("Status", self.status_combo)
        layout.addLayout(form)

        self.message_label = QLabel("")
        self.message_label.setStyleSheet("color: #fb7185; font: 700 11px 'Segoe UI';")
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label)

        button_bar = QFrame()
        button_bar.setObjectName("ButtonBar")
        button_layout = QHBoxLayout(button_bar)
        button_layout.setContentsMargins(0, 8, 0, 0)
        button_layout.setSpacing(10)
        button_layout.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save")
        save_btn.setObjectName("PrimaryButton")
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
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

    def _populate(self, employer):
        self.name_input.setText(employer.name)
        self.address_input.setText(employer.address)
        self.tin_input.setText(employer.tin)
        self._set_masked_value(self.sss_input, employer.sss_number, "00-0000000-0")
        self._set_masked_value(self.philhealth_input, employer.philhealth_number, "00-000000000-0")
        self._set_masked_value(self.hdmf_input, employer.hdmf_number, "0000-0000-0000")
        index = self.status_combo.findText(employer.status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)

    @staticmethod
    def _set_masked_value(widget: QLineEdit, digits: str, mask: str) -> None:
        value = "".join(char for char in str(digits) if char.isdigit())
        if not value:
            return
        if mask.startswith("00-0000000-0") and len(value) == 10:
            widget.setText(f"{value[:2]}-{value[2:9]}-{value[9:]}")
        elif mask.startswith("00-000000000-0") and len(value) == 12:
            widget.setText(f"{value[:2]}-{value[2:11]}-{value[11:]}")
        elif mask.startswith("0000-0000-0000") and len(value) == 12:
            widget.setText(f"{value[:4]}-{value[4:8]}-{value[8:]}")
        else:
            widget.setText(value)

    def set_error(self, message: str) -> None:
        self.message_label.setText(message)

    def form_values(self) -> dict[str, str]:
        return {
            "name": self.name_input.text().strip(),
            "address": self.address_input.text().strip(),
            "tin": self.tin_input.text().strip(),
            "sss_number": self.sss_input.text().strip(),
            "philhealth_number": self.philhealth_input.text().strip(),
            "hdmf_number": self.hdmf_input.text().strip(),
            "status": self.status_combo.currentText(),
        }


class EmployerAdminPanel(QWidget):
    def __init__(self, controller=None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.employers = []
        self._build_ui()
        self.refresh_employers()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        header = QLabel("Employer Management")
        header.setObjectName("Title")
        sub = QLabel("Add, edit, view, deactivate, or delete employers.")
        sub.setStyleSheet("color: #94a3b8;")
        layout.addWidget(header)
        layout.addWidget(sub)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "Name",
            "Address",
            "TIN",
            "SSS",
            "PhilHealth",
            "HDMF",
            "Status",
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setWordWrap(True)
        self.table.setStyleSheet(
            AppStyles.TABLE_BASE
            + AppStyles.TABLE_SCROLLBAR
            + """
            QTableWidget { border: none; border-radius: 14px; }
            QTableWidget::viewport { border-radius: 14px; }
            QHeaderView::section { background: rgba(2,6,23,0.78); color: #f8fafc; padding: 8px; border: none; font-weight: 700; }
            QTableWidget::item:selected { background: rgba(20,184,166,0.24); color: #ffffff; }
            QTableWidget::item:alternate { background: rgba(2,6,23,0.34); }
        """
        )
        table_header = self.table.horizontalHeader()
        table_header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        table_header.setStretchLastSection(True)
        table_header.setSectionResizeMode(QHeaderView.Stretch)
        self.table.setMinimumHeight(360)
        self.table.verticalHeader().setDefaultSectionSize(38)
        layout.addWidget(self.table, stretch=1)

        buttons = QHBoxLayout()
        self.add_btn = QPushButton("Add Employer")
        self.edit_btn = QPushButton("Edit Employer")
        self.deactivate_btn = QPushButton("Deactivate")
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setObjectName("DangerButton")
        self.refresh_btn = QPushButton("Refresh")

        self.add_btn.clicked.connect(self._add_employer)
        self.edit_btn.clicked.connect(self._edit_employer)
        self.deactivate_btn.clicked.connect(self._deactivate_employer)
        self.delete_btn.clicked.connect(self._delete_employer)
        self.refresh_btn.clicked.connect(self.refresh_employers)

        buttons.addWidget(self.add_btn)
        buttons.addWidget(self.edit_btn)
        buttons.addWidget(self.deactivate_btn)
        buttons.addWidget(self.delete_btn)
        buttons.addStretch()
        buttons.addWidget(self.refresh_btn)
        layout.addLayout(buttons)

    def refresh_employers(self):
        if self.controller is not None:
            self.employers = self.controller.list_all_employers(include_inactive=True)
        else:
            self.employers = []
        self._render_table()

    def _render_table(self):
        self.table.setRowCount(len(self.employers))
        for row, employer in enumerate(self.employers):
            values = [
                employer.name,
                employer.address,
                employer.tin,
                employer.sss_number,
                employer.philhealth_number,
                employer.hdmf_number,
                employer.status,
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value or ""))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, column, item)
            self.table.setRowHeight(row, 38)

    def _selected_employer(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.employers):
            return None
        return self.employers[row]

    def _add_employer(self):
        if self.controller is None:
            return
        dialog = EmployerFormDialog(self)
        if dialog.exec() != QDialog.Accepted:
            return
        try:
            values = dialog.form_values()
            self.controller.create_employer(**values)
        except ValueError as exc:
            dialog.set_error(str(exc))
            if dialog.exec() != QDialog.Accepted:
                return
            try:
                self.controller.create_employer(**dialog.form_values())
            except ValueError as retry_exc:
                GlassDialog(self, "Invalid Employer", str(retry_exc)).exec()
                return
        self.refresh_employers()

    def _edit_employer(self):
        employer = self._selected_employer()
        if employer is None or self.controller is None:
            return
        dialog = EmployerFormDialog(self, employer=employer)
        if dialog.exec() != QDialog.Accepted:
            return
        try:
            values = dialog.form_values()
            self.controller.update_employer(employer.id, **values)
        except ValueError as exc:
            GlassDialog(self, "Invalid Employer", str(exc)).exec()
            return
        self.refresh_employers()

    def _deactivate_employer(self):
        employer = self._selected_employer()
        if employer is None or self.controller is None:
            return
        try:
            self.controller.deactivate_employer(employer.id)
        except ValueError as exc:
            GlassDialog(self, "Deactivate Employer", str(exc)).exec()
            return
        self.refresh_employers()

    def _delete_employer(self):
        employer = self._selected_employer()
        if employer is None or self.controller is None:
            return
        dialog = GlassDialog(
            self,
            "Delete Employer",
            f"Delete employer '{employer.name}'?",
            buttons=[
                ("No", lambda: dialog.reject(), False),
                ("Yes", lambda: dialog.accept(), True),
            ],
        )
        if dialog.exec() != QDialog.Accepted:
            return
        try:
            self.controller.delete_employer(employer.id)
        except ValueError as exc:
            GlassDialog(self, "Delete Employer", str(exc)).exec()
            return
        self.refresh_employers()
