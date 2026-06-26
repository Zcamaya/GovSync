from PySide6.QtWidgets import QHBoxLayout, QStackedWidget, QVBoxLayout, QWidget, QLabel

from widgets.auth_windows import LoginPage, SuperAdminPage
from widgets.earnings_panel import EarningsPanel
from widgets.hdmf_loan_panel import HDMFLoanPanel
from widgets.philhealth_panel import PhilHealthPanel
from widgets.right_panel import RightPanelWidget
from widgets.sidebar import SidebarWidget
from widgets.sss_panel import SSSPanel
from widgets.workspace import WorkspaceWidget
from services.dashboard_service import set_refresh_callback


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


class PageFactory:
    def __init__(self, container):
        self.container = container

    def create_auth_pages(self):
        auth_controller = getattr(self.container, "auth_controller", None)
        login_page = LoginPage(controller=auth_controller)
        admin_page = SuperAdminPage(controller=auth_controller)
        return login_page, admin_page

    def create_app_page(self):
        sidebar_column = SidebarWidget()
        right_column = RightPanelWidget()
        workspace_stack = QStackedWidget()

        workspace_widget = WorkspaceWidget()
        workspace_stack.addWidget(workspace_widget)

        payroll_controller = getattr(self.container, "payroll_controller", None)
        earnings_panel = EarningsPanel(controller=payroll_controller)
        workspace_stack.addWidget(earnings_panel)

        philhealth_controller = getattr(self.container, "philhealth_controller", None)
        philhealth_panel = PhilHealthPanel(controller=philhealth_controller)
        workspace_stack.addWidget(philhealth_panel)

        workspace_stack.addWidget(
            GenericPlaceholderPage("HDMF - Contribution Portal (Coming Soon)")
        )

        sss_controller = getattr(self.container, "sss_controller", None)
        hdmf_controller = getattr(self.container, "hdmf_controller", None)
        sss_panel = SSSPanel(controller=sss_controller)
        hdmf_panel = HDMFLoanPanel(controller=hdmf_controller)
        workspace_stack.addWidget(sss_panel)
        workspace_stack.addWidget(hdmf_panel)

        set_refresh_callback(workspace_widget.refresh_stats)

        app_page = QWidget()
        app_page.setStyleSheet("background: transparent; border: none;")

        content_layout = QHBoxLayout(app_page)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(20)
        content_layout.addWidget(sidebar_column)
        content_layout.addWidget(workspace_stack, stretch=1)
        content_layout.addWidget(right_column)

        return (
            app_page,
            sidebar_column,
            right_column,
            workspace_stack,
            workspace_widget,
            earnings_panel,
            philhealth_panel,
            sss_panel,
            hdmf_panel,
        )
