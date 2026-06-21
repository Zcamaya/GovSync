from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from utils.dashboard_stats import get_all_past_month_totals
from widgets.glass_panel import TrueGlassPanel


class WorkspaceWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
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
        self.welcome_title.setStyleSheet(
            "color: #34d399; font-size: 24px; font-weight: 800; border: none; background: transparent;"
        )
        self.welcome_subtitle = QLabel("Your compliance workspace is ready.")
        self.welcome_subtitle.setStyleSheet(
            "color: #cbd5e1; font-size: 12px; border: none; background: transparent;"
        )
        self.banner_layout.addStretch()
        self.banner_layout.addWidget(self.welcome_title)
        self.banner_layout.addWidget(self.welcome_subtitle)
        self.banner_layout.addStretch()

        stats_container = QHBoxLayout()
        stats_container.setSpacing(15)

        self.philhealth_box = TrueGlassPanel(border_radius=15)
        philhealth_layout = QVBoxLayout(self.philhealth_box)
        philhealth_layout.addWidget(QLabel("Philhealth (Past Month Total)"))
        self.lbl_ph_count = QLabel("0")
        self.lbl_ph_count.setStyleSheet(
            "color: #34d399; font-size: 28px; font-weight: 800; border: none; background: transparent;"
        )
        philhealth_layout.addWidget(self.lbl_ph_count)

        self.hdmf_box = TrueGlassPanel(border_radius=15)
        hdmf_layout = QVBoxLayout(self.hdmf_box)
        hdmf_layout.addWidget(QLabel("HDMF (Past Month Total)"))
        self.lbl_hd_count = QLabel("0")
        self.lbl_hd_count.setStyleSheet(
            "color: #34d399; font-size: 28px; font-weight: 800; border: none; background: transparent;"
        )
        hdmf_layout.addWidget(self.lbl_hd_count)

        self.sss_box = TrueGlassPanel(border_radius=15)
        sss_layout = QVBoxLayout(self.sss_box)
        sss_layout.addWidget(QLabel("SSS (Past Month Total)"))
        self.lbl_sss_count = QLabel("0")
        self.lbl_sss_count.setStyleSheet(
            "color: #34d399; font-size: 28px; font-weight: 800; border: none; background: transparent;"
        )
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
        totals = get_all_past_month_totals()
        self.lbl_ph_count.setText(str(totals["philhealth"]))
        self.lbl_hd_count.setText(str(totals["hdmf"]))
        self.lbl_sss_count.setText(str(totals["sss"]))
