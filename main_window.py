from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizeGrip,
    QSizePolicy,
    QSpacerItem,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from widgets.earnings_panel import EarningsPanel
from widgets.auth_windows import LoginPage, SuperAdminPage
from widgets.glass_dialog import GlassDialog
from widgets.hdmf_loan_panel import HDMFLoanPanel
from widgets.philhealth_panel import PhilHealthPanel
from widgets.right_panel import RightPanelWidget
from widgets.sidebar import SidebarWidget
from widgets.sss_panel import SSSPanel
from widgets.workspace import WorkspaceWidget
from utils.account_store import get_account
from utils.dashboard_stats import set_refresh_callback
from utils.ui_icons import set_exit_icon, set_maximize_icon, set_minimize_icon


class GenericPlaceholderPage(QWidget):
    def __init__(self, title_text):
        super().__init__()

        layout = QVBoxLayout(self)
        label = QLabel(title_text)
        label.setStyleSheet(
            "color: #ffffff; font-size: 20px; font-weight: bold; border: none;"
        )
        layout.addWidget(label)
        layout.addStretch()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(1024, 650)
        self.resize(1280, 750)

        self.container = QFrame()
        self.container.setObjectName("MainContainer")
        self.setCentralWidget(self.container)
        self.container.setStyleSheet("""
            #MainContainer {
                background: qradialgradient(cx:0.3, cy:0.2, radius:1.4, fx:0.3, fy:0.2,
                                            stop:0 #0a1f1a, stop:0.5 #070b12, stop:1 #020408);
                border: 1px solid rgba(20, 184, 166, 0.16);
                border-radius: 20px;
            }
            QLabel {
                font-family: 'Segoe UI', sans-serif;
                background: transparent;
                color: white;
            }
            QScrollBar:vertical {
                background: rgba(2, 6, 23, 0.18);
                border: none;
                border-radius: 6px;
                width: 12px;
                margin: 3px;
            }
            QScrollBar::handle:vertical {
                background: rgba(148, 163, 184, 0.46);
                border-radius: 6px;
                min-height: 24px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(20, 184, 166, 0.72);
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
                border: none;
                height: 0;
            }
            QScrollBar:horizontal {
                background: rgba(2, 6, 23, 0.18);
                border: none;
                border-radius: 6px;
                height: 12px;
                margin: 3px;
            }
            QScrollBar::handle:horizontal {
                background: rgba(148, 163, 184, 0.46);
                border-radius: 6px;
                min-width: 24px;
            }
            QScrollBar::handle:horizontal:hover {
                background: rgba(20, 184, 166, 0.72);
            }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal,
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: transparent;
                border: none;
                width: 0;
            }
        """)

        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(10, 0, 10, 0)
        header_layout.addSpacerItem(
            QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )

        btn_min = self.create_btn("", "#64748b")
        btn_max = self.create_btn("", "#64748b")
        btn_close = self.create_btn("", "rgba(244, 63, 94, 0.16)")
        btn_min.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                padding: 0;
            }
            QPushButton:hover {
                background: rgba(15, 23, 42, 0.55);
            }
        """)
        set_minimize_icon(btn_min, "#94a3b8", 13)
        set_maximize_icon(btn_max, "#94a3b8", 11)
        set_exit_icon(btn_close, "#f43f5e", 11)

        btn_min.clicked.connect(self.showMinimized)
        btn_max.clicked.connect(self.toggle_maximized)
        btn_close.clicked.connect(self.close)

        header_layout.addWidget(btn_min)
        header_layout.addWidget(btn_max)
        header_layout.addWidget(btn_close)
        main_layout.addLayout(header_layout)

        self.page_stack = QStackedWidget()
        self.page_stack.setStyleSheet("background: transparent; border: none;")
        main_layout.addWidget(self.page_stack, stretch=1)

        grip_layout = QHBoxLayout()
        grip_layout.setContentsMargins(0, 0, 4, 2)
        grip_layout.addStretch()
        grip_layout.addWidget(QSizeGrip(self.container))
        main_layout.addLayout(grip_layout)

        self.login_page = LoginPage()
        self.admin_page = SuperAdminPage()
        self.app_page = self._create_app_page()

        self.login_page.authenticated.connect(self._on_authenticated)
        self.admin_page.logout_requested.connect(self._show_login)

        self.page_stack.addWidget(self.login_page)
        self.page_stack.addWidget(self.admin_page)
        self.page_stack.addWidget(self.app_page)
        self.page_stack.setCurrentWidget(self.login_page)
        self.drag_pos = QPoint()

    def _create_app_page(self):
        app_page = QWidget()
        app_page.setStyleSheet("background: transparent; border: none;")

        content_layout = QHBoxLayout(app_page)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(20)

        self.sidebar_column = SidebarWidget()
        self.sidebar_column.logout_requested.connect(self._show_login)
        self.right_column = RightPanelWidget()

        self.workspace_stack = QStackedWidget()
        self.workspace_widget = WorkspaceWidget()
        self.workspace_stack.addWidget(self.workspace_widget)
        self.workspace_stack.addWidget(EarningsPanel())
        self.philhealth_panel = PhilHealthPanel()
        self.workspace_stack.addWidget(self.philhealth_panel)
        self.workspace_stack.addWidget(
            GenericPlaceholderPage("HDMF - Contribution Portal (Coming Soon)")
        )
        self.workspace_stack.addWidget(SSSPanel())
        self.workspace_stack.addWidget(HDMFLoanPanel())
        self.workspace_stack.addWidget(GenericPlaceholderPage("SSS Loan Processing"))
        self.workspace_stack.addWidget(GenericPlaceholderPage("Master Calendar Schedule"))

        self.sss_panel = self.workspace_stack.widget(4)

        set_refresh_callback(self.workspace_widget.refresh_stats)

        self.sidebar_column.list_widget.currentRowChanged.connect(
            self._on_sidebar_changed
        )

        content_layout.addWidget(self.sidebar_column)
        content_layout.addWidget(self.workspace_stack, stretch=1)
        content_layout.addWidget(self.right_column)

        return app_page

    def _on_sidebar_changed(self, index):
        self.workspace_stack.setCurrentIndex(index)
        if index == 0:
            self.workspace_widget.refresh_stats()

    def _on_authenticated(self, role, username):
        if role == "admin":
            self.admin_page._load_accounts()
            self.page_stack.setCurrentWidget(self.admin_page)
            return

        account = get_account(username) or {"username": username}
        self.right_column.set_account(account)
        self.philhealth_panel.set_account(username)
        self.workspace_widget.set_account_name(account.get("username", username))
        if hasattr(self.sss_panel, "set_account"):
            self.sss_panel.set_account(account)
        self.page_stack.setCurrentWidget(self.app_page)

    def _show_login(self):
        self.sidebar_column.list_widget.setCurrentRow(0)
        if hasattr(self.login_page, "_reset_messages"):
            self.login_page._reset_messages()
        if hasattr(self.login_page, "stack"):
            self.login_page.stack.setCurrentIndex(0)
        self.page_stack.setCurrentWidget(self.login_page)

    def create_btn(self, text, hover_color):
        btn = QPushButton(text)
        btn.setFixedSize(18, 18)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(15, 23, 42, 0.78);
                color: #94a3b8;
                border: 1px solid rgba(148, 163, 184, 0.18);
                border-radius: 4px;
                padding: 0;
            }}
            QPushButton:hover {{
                background: {hover_color};
                color: white;
            }}
        """)
        return btn

    def toggle_maximized(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            next_pos = self.pos() + event.globalPosition().toPoint() - self.drag_pos
            self.move(next_pos)
            self.drag_pos = event.globalPosition().toPoint()

    def closeEvent(self, event):
        """Confirm all close attempts, including the title button and Alt+F4."""
        dialog = GlassDialog(
            self,
            "Exit Application",
            "Are you sure you want to quit?",
            buttons=[
                ("No", lambda: dialog.reject(), False),
                ("Yes", lambda: dialog.accept(), True),
            ],
        )

        if dialog.exec() == GlassDialog.Accepted:
            event.accept()
        else:
            event.ignore()
