from PySide6.QtWidgets import QHBoxLayout, QStackedWidget, QVBoxLayout, QWidget, QLabel, QSplitter
from PySide6.QtCore import Qt

from widgets.auth_windows import LoginPage, SuperAdminPage
from constants.styles import AppStyles
from widgets.earnings_panel import EarningsPanel
from widgets.employee_records_panel import EmployeeRecordsPanel
from widgets.hdmf_loan_panel import HDMFLoanPanel
from widgets.philhealth_panel import PhilHealthPanel
from widgets.right_panel import RightPanelWidget
from widgets.sidebar import SidebarWidget
from widgets.sss_panel import SSSPanel
from widgets.workspace import WorkspaceWidget



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


class SafeSplitter(QSplitter):
    """QSplitter subclass that guards against invalid maximum size values.

    Some runtime conditions may cause Qt to receive invalid negative maximum
    size values which emit warnings. This subclass clamps any negative
    width/height for maximum size calls to zero to avoid those warnings.
    """
    def setMaximumSize(self, w: int, h: int = None):
        try:
            if h is None:
                # PySide overload may pass a QSize; delegate to base safely
                return super().setMaximumSize(w)
            cw = int(w) if isinstance(w, (int, float)) else int(w or 0)
            ch = int(h) if isinstance(h, (int, float)) else int(h or 0)
            cw = max(0, cw)
            ch = max(0, ch)
            return super().setMaximumSize(cw, ch)
        except Exception:
            try:
                return super().setMaximumSize(max(0, int(w or 0)), max(0, int(h or 0)))
            except Exception:
                return super().setMaximumSize(16777215, 16777215)


class PageFactory:
    def __init__(self, container):
        self.container = container

    def create_auth_pages(self):
        auth_controller = getattr(self.container, "auth_controller", None)
        employer_controller = getattr(self.container, "employer_controller", None)
        login_page = LoginPage(controller=auth_controller, employer_controller=employer_controller)
        admin_page = SuperAdminPage(controller=auth_controller, employer_controller=employer_controller)
        return login_page, admin_page

    def create_app_page(self):
        sidebar_column = SidebarWidget()
        right_column = RightPanelWidget()
        workspace_stack = QStackedWidget()
        workspace_stack.setObjectName("WorkspaceStack")
        workspace_stack.setStyleSheet("""
            QStackedWidget#WorkspaceStack {
                border-radius: 18px;
            }
        """)

        workspace_widget = WorkspaceWidget(dashboard_service=self.container.dashboard_service)
        workspace_stack.addWidget(workspace_widget)

        payroll_controller = getattr(self.container, "payroll_controller", None)
        earnings_panel = EarningsPanel(controller=payroll_controller, dashboard_service=self.container.dashboard_service)
        workspace_stack.addWidget(earnings_panel)

        employee_records_controller = getattr(self.container, "employee_records_controller", None)
        employee_records_panel = EmployeeRecordsPanel(controller=employee_records_controller)
        workspace_stack.addWidget(employee_records_panel)

        philhealth_controller = getattr(self.container, "philhealth_controller", None)
        philhealth_panel = PhilHealthPanel(controller=philhealth_controller)
        workspace_stack.addWidget(philhealth_panel)

        workspace_stack.addWidget(
            GenericPlaceholderPage("HDMF - Contribution Portal (Coming Soon)")
        )

        sss_controller = getattr(self.container, "sss_controller", None)
        hdmf_controller = getattr(self.container, "hdmf_controller", None)
        sss_panel = SSSPanel(controller=sss_controller, dashboard_service=self.container.dashboard_service)
        hdmf_panel = HDMFLoanPanel(controller=hdmf_controller)
        workspace_stack.addWidget(sss_panel)
        workspace_stack.addWidget(hdmf_panel)

        self.container.dashboard_service.register_refresh_callback(workspace_widget.refresh_stats)

        app_page = QWidget()
        app_page.setObjectName("AppPage")
        app_page.setAttribute(Qt.WA_StyledBackground, True)
        app_page.setStyleSheet("""
            QWidget#AppPage {
                background: transparent;
                border-radius: 20px;
            }
        """)

        content_layout = QHBoxLayout(app_page)
        content_layout.setContentsMargins(AppStyles.SECTION_PADDING, AppStyles.SECTION_PADDING, AppStyles.SECTION_PADDING, AppStyles.SECTION_PADDING)
        content_layout.setSpacing(AppStyles.PANEL_SPACING)

        splitter = SafeSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(AppStyles.INNER_PADDING // 2 + 2)
        splitter.setOpaqueResize(True)
        splitter.addWidget(workspace_stack)
        splitter.addWidget(right_column)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)

        content_layout.addWidget(sidebar_column)
        content_layout.addWidget(splitter, stretch=1)

        return (
            app_page,
            sidebar_column,
            right_column,
            workspace_stack,
            workspace_widget,
            earnings_panel,
            employee_records_panel,
            philhealth_panel,
            sss_panel,
            hdmf_panel,
        )
