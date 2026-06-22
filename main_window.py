from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QIcon
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
from utils.account_store import get_account, get_active_account, set_active_account
from utils.dashboard_stats import set_refresh_callback
from utils.ui_icons import set_exit_icon, set_maximize_icon, set_minimize_icon
from config import APP_NAME, DEFAULT_WINDOW_HEIGHT, DEFAULT_WINDOW_WIDTH, MIN_WINDOW_HEIGHT, MIN_WINDOW_WIDTH
from utils.resources import asset_path


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
    def __init__(self, container=None):
        super().__init__()
        self.app_container = container

        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(asset_path("icon.ico")))
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)

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
        header_layout.setContentsMargins(12, 2, 12, 0)
        header_layout.setSpacing(6)
        header_layout.addSpacerItem(
            QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )

        btn_min = self.create_window_btn("minimize.svg", "#94a3b8", 14)
        btn_max = self.create_window_btn("maximize.svg", "#94a3b8", 12)
        btn_close = self.create_window_btn("exit.svg", "#f43f5e", 12, hover_color="rgba(244, 63, 94, 0.16)")

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

        auth_controller = getattr(self.app_container, "auth_controller", None)
        self.login_page = LoginPage(controller=auth_controller)
        self.admin_page = SuperAdminPage(controller=auth_controller)
        self.app_page = self._create_app_page()

        self.login_page.authenticated.connect(self._on_authenticated)
        self.admin_page.logout_requested.connect(self._show_login)

        self.page_stack.addWidget(self.login_page)
        self.page_stack.addWidget(self.admin_page)
        self.page_stack.addWidget(self.app_page)
        active_account = get_active_account() or {}
        if active_account.get("username") and active_account.get("username") != "superadmin":
            self._on_authenticated("user", active_account["username"])
        else:
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
        payroll_controller = getattr(self.app_container, "payroll_controller", None)
        self.earnings_panel = EarningsPanel(controller=payroll_controller)
        self.workspace_stack.addWidget(self.earnings_panel)
        philhealth_controller = getattr(self.app_container, "philhealth_controller", None)
        self.philhealth_panel = PhilHealthPanel(controller=philhealth_controller)
        self.workspace_stack.addWidget(self.philhealth_panel)
        self.workspace_stack.addWidget(
            GenericPlaceholderPage("HDMF - Contribution Portal (Coming Soon)")
        )
        sss_controller = getattr(self.app_container, "sss_controller", None)
        hdmf_controller = getattr(self.app_container, "hdmf_controller", None)
        self.sss_panel = SSSPanel(controller=sss_controller)
        self.hdmf_panel = HDMFLoanPanel(controller=hdmf_controller)
        self.workspace_stack.addWidget(self.sss_panel)
        self.workspace_stack.addWidget(self.hdmf_panel)

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
        self.philhealth_panel.set_account(account)
        self.workspace_widget.set_account_name(account.get("username", username))
        if hasattr(self.earnings_panel, "set_account"):
            self.earnings_panel.set_account(account)
        if hasattr(self.sss_panel, "set_account"):
            self.sss_panel.set_account(account)
        if hasattr(self.hdmf_panel, "set_account"):
            self.hdmf_panel.set_account(account)
        self.page_stack.setCurrentWidget(self.app_page)

    def _show_login(self):
        set_active_account(None)
        self.sidebar_column.list_widget.setCurrentRow(0)
        if hasattr(self.login_page, "_reset_messages"):
            self.login_page._reset_messages()
        if hasattr(self.login_page, "stack"):
            self.login_page.stack.setCurrentIndex(0)
        self.page_stack.setCurrentWidget(self.login_page)

    def create_window_btn(self, icon_name, color, icon_size, hover_color="rgba(15, 23, 42, 0.55)"):
        btn = QPushButton()
        btn.setFixedSize(22, 22)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFlat(True)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                padding: 0;
                margin: 0;
            }}
            QPushButton:hover {{
                background: {hover_color};
                border: none;
                border-radius: 4px;
            }}
        """)
        if icon_name == "minimize.svg":
            set_minimize_icon(btn, color, icon_size)
        elif icon_name == "maximize.svg":
            set_maximize_icon(btn, color, icon_size)
        else:
            set_exit_icon(btn, color, icon_size)
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
