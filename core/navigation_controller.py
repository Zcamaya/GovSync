from core.session_manager import get_active_account, set_active_account
from services.auth_manager import get_account


class NavigationController:
    def __init__(
        self,
        page_stack,
        sidebar_column,
        right_column,
        workspace_stack,
        workspace_widget,
        earnings_panel,
        philhealth_panel,
        sss_panel,
        hdmf_panel,
        login_page,
        admin_page,
        app_page,
    ):
        self.page_stack = page_stack
        self.sidebar_column = sidebar_column
        self.right_column = right_column
        self.workspace_stack = workspace_stack
        self.workspace_widget = workspace_widget
        self.earnings_panel = earnings_panel
        self.philhealth_panel = philhealth_panel
        self.sss_panel = sss_panel
        self.hdmf_panel = hdmf_panel
        self.login_page = login_page
        self.admin_page = admin_page
        self.app_page = app_page

    def bind(self):
        self.login_page.authenticated.connect(self.on_authenticated)
        self.admin_page.logout_requested.connect(self.show_login)
        self.sidebar_column.list_widget.currentRowChanged.connect(
            self.on_sidebar_changed
        )

    def on_sidebar_changed(self, index):
        self.page_stack.setCurrentIndex(self.page_stack.indexOf(self.app_page))
        self.workspace_stack.setCurrentIndex(index)
        if index == 0:
            self.workspace_widget.refresh_stats()

    def on_authenticated(self, role, username):
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

    def show_login(self):
        set_active_account(None)
        self.sidebar_column.list_widget.setCurrentRow(0)
        if hasattr(self.login_page, "_reset_messages"):
            self.login_page._reset_messages()
        if hasattr(self.login_page, "stack"):
            self.login_page.stack.setCurrentIndex(0)
        self.page_stack.setCurrentWidget(self.login_page)

    def initial_authentication(self):
        active_account = get_active_account() or {}
        if active_account.get("username") and active_account.get("username") != "superadmin":
            self.on_authenticated("user", active_account["username"])
        else:
            self.page_stack.setCurrentWidget(self.login_page)
