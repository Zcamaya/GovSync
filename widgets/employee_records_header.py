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
        self._compact_mode = False
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(AppStyles.PANEL_SPACING)

        self.stats_panel = TrueGlassPanel(border_radius=16)
        self.stats_panel.setStyleSheet(
            self.stats_panel.styleSheet() + f"QFrame {{ border: 1px solid {AppStyles.PANEL_BORDER_SUBTLE}; }}"
        )
        stats_layout = QHBoxLayout(self.stats_panel)
        stats_layout.setContentsMargins(AppStyles.SECTION_PADDING, AppStyles.SECTION_PADDING, AppStyles.SECTION_PADDING, AppStyles.SECTION_PADDING)
        stats_layout.setSpacing(AppStyles.INNER_PADDING)

        self.stats_cards = []
        for label in [
            "Total Employees",
            "Total Clients",
            "Total Payroll Imports",
            "Last Imported Payroll",
        ]:
            card = QFrame()
            card.setStyleSheet(AppStyles.TABLE_STAT_CARD)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(12, 12, 12, 12)
            card_layout.setSpacing(6)

            title = QLabel(label)
            title.setStyleSheet(AppStyles.TABLE_METADATA_TEXT)
            value = QLabel("0")
            value.setStyleSheet(AppStyles.METRIC_VALUE.replace("28px", "22px"))

            card_layout.addWidget(title)
            card_layout.addWidget(value)
            stats_layout.addWidget(card)
            self.stats_cards.append((title, value))

        layout.addWidget(self.stats_panel)

        filters_panel = TrueGlassPanel(border_radius=16)
        filters_panel.setStyleSheet(
            filters_panel.styleSheet() + f"QFrame {{ border: 1px solid {AppStyles.PANEL_BORDER_SUBTLE}; }}"
        )
        filters_layout = QHBoxLayout(filters_panel)
        filters_layout.setContentsMargins(AppStyles.SECTION_PADDING, AppStyles.SECTION_PADDING, AppStyles.SECTION_PADDING, AppStyles.SECTION_PADDING)
        filters_layout.setSpacing(AppStyles.INNER_PADDING)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search employee")
        self.search_input.setMinimumHeight(38)
        self.search_input.setStyleSheet(AppStyles.TABLE_SEARCH_INPUT)
        filters_layout.addWidget(self.search_input, stretch=1)

        self.employer_combo = QComboBox()
        self.employer_combo.addItem("Employer")
        self.employer_combo.setMinimumHeight(38)
        filters_layout.addWidget(self.employer_combo)

        self.client_combo = QComboBox()
        self.client_combo.addItem("Client")
        self.client_combo.setMinimumHeight(38)
        filters_layout.addWidget(self.client_combo)

        self.applicable_month_combo = QComboBox()
        self.applicable_month_combo.addItem("Applicable Month")
        self.applicable_month_combo.setMinimumHeight(38)
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
        self.filters_panel = filters_panel

    def set_compact_mode(self, enabled: bool):
        if self._compact_mode == enabled:
            return

        self._compact_mode = enabled
        if enabled:
            self.layout().setSpacing(AppStyles.PANEL_SPACING_COMPACT)
            self.stats_panel.layout().setContentsMargins(12, 12, 12, 12)
            for card in self.stats_cards:
                title, value = card
                title.setStyleSheet(AppStyles.TABLE_METADATA_TEXT.replace("11px", "10px"))
                value.setStyleSheet(AppStyles.METRIC_VALUE.replace("28px", "20px"))

            filters_layout = self.filters_panel.layout()
            filters_layout.setContentsMargins(12, 12, 12, 12)
            filters_layout.setSpacing(AppStyles.INNER_PADDING - 4)
            self.search_input.setMinimumHeight(32)
            self.employer_combo.setMinimumHeight(32)
            self.client_combo.setMinimumHeight(32)
            self.applicable_month_combo.setMinimumHeight(32)
        else:
            self.layout().setSpacing(AppStyles.PANEL_SPACING)
            self.stats_panel.layout().setContentsMargins(18, 18, 18, 18)
            for card in self.stats_cards:
                title, value = card
                title.setStyleSheet(AppStyles.TABLE_METADATA_TEXT)
                value.setStyleSheet(AppStyles.METRIC_VALUE.replace("28px", "22px"))

            filters_layout = self.filters_panel.layout()
            filters_layout.setContentsMargins(AppStyles.SECTION_PADDING, AppStyles.SECTION_PADDING, AppStyles.SECTION_PADDING, AppStyles.SECTION_PADDING)
            filters_layout.setSpacing(AppStyles.INNER_PADDING - 2)
            self.search_input.setMinimumHeight(38)
            self.employer_combo.setMinimumHeight(38)
            self.client_combo.setMinimumHeight(38)
            self.applicable_month_combo.setMinimumHeight(38)

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
