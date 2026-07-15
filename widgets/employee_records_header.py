from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from constants.styles import AppStyles
from widgets.glass_panel import TrueGlassPanel


class EmployeeRecordsHeader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        self.stats_panel = TrueGlassPanel(border_radius=16)
        stats_layout = QHBoxLayout(self.stats_panel)
        stats_layout.setContentsMargins(18, 18, 18, 18)
        stats_layout.setSpacing(12)

        self.stats_cards = []
        for label in [
            "Total Employees",
            "Total Clients",
            "Total Payroll Imports",
            "Last Imported Payroll",
        ]:
            card = QFrame()
            card.setStyleSheet(
                "background: rgba(15, 23, 42, 0.55); border: 1px solid rgba(255,255,255,0.08); border-radius: 14px;"
            )
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(12, 12, 12, 12)
            card_layout.setSpacing(6)

            title = QLabel(label)
            title.setStyleSheet("color: #cbd5e1; font-size: 12px;")
            value = QLabel("0")
            value.setStyleSheet("color: #34d399; font-size: 22px; font-weight: 700;")

            card_layout.addWidget(title)
            card_layout.addWidget(value)
            stats_layout.addWidget(card)
            self.stats_cards.append((title, value))

        layout.addWidget(self.stats_panel)

        filters_panel = TrueGlassPanel(border_radius=16)
        filters_layout = QHBoxLayout(filters_panel)
        filters_layout.setContentsMargins(16, 16, 16, 16)
        filters_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search employee")
        self.search_input.setStyleSheet(
            "QLineEdit { background: rgba(15,23,42,0.75); color: white; border: 1px solid rgba(255,255,255,0.14); border-radius: 8px; padding: 8px 10px; }"
        )
        filters_layout.addWidget(self.search_input, stretch=1)

        self.employer_combo = QComboBox()
        self.employer_combo.addItem("Employer")
        filters_layout.addWidget(self.employer_combo)

        self.client_combo = QComboBox()
        self.client_combo.addItem("Client")
        filters_layout.addWidget(self.client_combo)

        self.applicable_month_combo = QComboBox()
        self.applicable_month_combo.addItem("Applicable Month")
        filters_layout.addWidget(self.applicable_month_combo)

        combo_style = AppStyles.GLOBAL_DROPDOWN
        for cb in (
            self.employer_combo,
            self.client_combo,
            self.applicable_month_combo,
        ):
            cb.setStyleSheet(combo_style)
            cb.setFocusPolicy(Qt.NoFocus)
            try:
                view = cb.view()
                view.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
            except Exception:
                pass
            cb.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        layout.addWidget(filters_panel)

    def set_stats(self, stats: dict):
        labels = ["total_employees", "total_clients", "total_imports", "last_imported"]
        for (_, value_label), key in zip(self.stats_cards, labels):
            value = stats.get(key, "")
            if key == "last_imported" and value:
                value = str(value)
            value_label.setText(str(value))

    def set_filter_options(self, options: dict):
        self._set_combo_items(
            self.employer_combo,
            ["Employer"] + options.get("employers", []),
            self.employer_combo.currentText(),
        )
        self._set_combo_items(
            self.client_combo,
            ["Client"] + options.get("clients", []),
            self.client_combo.currentText(),
        )
        self._set_combo_items(
            self.applicable_month_combo,
            ["Applicable Month"] + options.get("applicable_months", []),
            self.applicable_month_combo.currentText(),
        )

    def _set_combo_items(self, combo, values, current_value):
        current = current_value if current_value in values else values[0] if values else ""
        combo.blockSignals(True)
        combo.clear()
        combo.addItems(values)
        combo.setCurrentText(current)
        combo.blockSignals(False)
