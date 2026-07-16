from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from constants.styles import AppStyles
from widgets.glass_panel import TrueGlassPanel


class WorkspaceWidget(QWidget):
    def __init__(self, parent=None, dashboard_service=None):
        super().__init__(parent)
        self.dashboard_service = dashboard_service
        self.account_name = "Account"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        welcome_banner = TrueGlassPanel(border_radius=20)
        welcome_banner.setFixedHeight(125)
        self.banner_layout = QVBoxLayout(welcome_banner)
        self.banner_layout.setContentsMargins(18, 18, 18, 18)
        self.banner_layout.setSpacing(6)

        self.welcome_title = QLabel()
        self.welcome_title.setStyleSheet("color: #34d399; font: 800 24px 'Segoe UI'; border: none; background: transparent;")
        self.welcome_subtitle = QLabel("Your compliance workspace is ready.")
        self.welcome_subtitle.setStyleSheet(AppStyles.SECTION_SUBTITLE)
        self.banner_layout.addStretch()
        self.banner_layout.addWidget(self.welcome_title)
        self.banner_layout.addWidget(self.welcome_subtitle)
        self.banner_layout.addStretch()

        stats_container = QHBoxLayout()
        stats_container.setSpacing(15)

        self.philhealth_box = TrueGlassPanel(border_radius=15)
        philhealth_layout = QVBoxLayout(self.philhealth_box)
        philhealth_label = QLabel("Philhealth (Past Month Total)")
        philhealth_label.setStyleSheet(AppStyles.SECTION_SUBTITLE)
        philhealth_layout.addWidget(philhealth_label)
        self.lbl_ph_count = QLabel("0")
        self.lbl_ph_count.setStyleSheet(AppStyles.METRIC_VALUE)
        philhealth_layout.addWidget(self.lbl_ph_count)

        self.hdmf_box = TrueGlassPanel(border_radius=15)
        hdmf_layout = QVBoxLayout(self.hdmf_box)
        hdmf_label = QLabel("HDMF (Past Month Total)")
        hdmf_label.setStyleSheet(AppStyles.SECTION_SUBTITLE)
        hdmf_layout.addWidget(hdmf_label)
        self.lbl_hd_count = QLabel("0")
        self.lbl_hd_count.setStyleSheet(AppStyles.METRIC_VALUE)
        hdmf_layout.addWidget(self.lbl_hd_count)

        self.sss_box = TrueGlassPanel(border_radius=15)
        sss_layout = QVBoxLayout(self.sss_box)
        sss_label = QLabel("SSS (Past Month Total)")
        sss_label.setStyleSheet(AppStyles.SECTION_SUBTITLE)
        sss_layout.addWidget(sss_label)
        self.lbl_sss_count = QLabel("0")
        self.lbl_sss_count.setStyleSheet(AppStyles.METRIC_VALUE)
        sss_layout.addWidget(self.lbl_sss_count)

        stats_container.addWidget(self.philhealth_box)
        stats_container.addWidget(self.hdmf_box)
        stats_container.addWidget(self.sss_box)

        layout.addWidget(welcome_banner)
        layout.addLayout(stats_container)

        self.set_account_name(self.account_name)

    def set_account_name(self, account_name):
        self.account_name = account_name or "Account"
        self.welcome_title.setText(f"Welcome, {self.account_name}")
        self.refresh_stats()

    def refresh_stats(self):
        if self.dashboard_service is None:
            self.lbl_ph_count.setText("0")
            self.lbl_hd_count.setText("0")
            self.lbl_sss_count.setText("0")
            return

        totals = self.dashboard_service.get_all_past_month_totals()
        self.lbl_ph_count.setText(str(totals.get("philhealth", 0)))
        self.lbl_hd_count.setText(str(totals.get("hdmf", 0)))
        self.lbl_sss_count.setText(str(totals.get("sss", 0)))
