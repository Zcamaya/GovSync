import os

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QFont, QImage, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from widgets.glass_dialog import GlassDialog
from widgets.employer_admin_panel import EmployerAdminPanel
from widgets.right_panel import RightPanelWidget
from controllers.auth_controller import AuthController
from services.auth_manager import (
    authenticate,
    delete_account,
    load_accounts,
    register_account,
    SUPER_ADMIN_USERNAME,
)
from shared.resources import asset_path
from shared.ui import set_exit_icon
from constants.styles import AppStyles
from widgets.shared_table import RoundedTableCard, SharedTable


def _populate_employer_combo(combo, employer_controller):
    combo.clear()
    combo.addItem("", None)
    if employer_controller is None:
        return
    try:
        employers = employer_controller.list_active_employers() or []
    except Exception:
        employers = []
    for employer in employers:
        combo.addItem(employer.name, employer.id)


def _selected_employer_data(combo):
    return combo.currentText().strip(), combo.currentData()


def _register_account_flow(controller, username, password, employer_name, employer_id):
    if controller:
        controller.register(
            username,
            password,
            "",
            "",
            "",
            employer_name,
            employer_id,
        )
    else:
        register_account(
            username,
            password,
            "",
            "",
            "",
            employer_name,
            employer_id,
        )


def logo_pixmap(size):
    logo_path = asset_path("logo.svg")
    image = QImage(size, size, QImage.Format_ARGB32)
    image.fill(Qt.transparent)
    if os.path.exists(logo_path):
        painter = QPainter(image)
        QSvgRenderer(logo_path).render(painter)
        painter.end()
    return QPixmap.fromImage(image)


SHELL_STYLE = """
    QFrame#AuthShell {
        background: qradialgradient(cx:0.3, cy:0.2, radius:1.4, fx:0.3, fy:0.2,
                                    stop:0 #0a1f1a, stop:0.5 #070b12, stop:1 #020408);
        border: none;
        border-radius: 20px;
    }
    QFrame#BrandPanel {
        background: transparent;
        border: none;
    }
    QFrame#AuthCard {
        background: rgba(2, 6, 23, 0.54);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 16px;
    }
    QFrame#AuthArtPanel {
        background: rgba(20, 43, 37, 0.72);
        border: none;
        border-top-left-radius: 16px;
        border-bottom-left-radius: 16px;
    }
    QFrame#FormPanel, QFrame#ContentPanel {
        background: rgba(20, 43, 37, 0.64);
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 12px;
    }
    QFrame#AuthCard QFrame#FormPanel {
        background: rgba(15, 23, 42, 0.82);
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 12px;
    }
    QFrame#AuthCard QFrame#FormPanel QLabel {
        color: #cbd5e1;
    }
    QFrame#AuthCard QFrame#FormPanel QLabel#Title {
        color: #f8fafc;
        font: 800 20px 'Segoe UI';
    }
    QFrame#AuthCard QFrame#FormPanel QLineEdit {
        background: rgba(2, 6, 23, 0.62);
        border: 1px solid rgba(148, 163, 184, 0.24);
        border-radius: 10px;
        color: #e5e7eb;
        min-height: 38px;
        padding: 0 12px;
        font: 12px 'Segoe UI';
    }
    QFrame#AuthCard QFrame#FormPanel QLineEdit:focus {
        border-color: rgba(45, 212, 191, 0.65);
    }
    QFrame#AuthCard QFrame#FormPanel QPushButton {
        border-radius: 10px;
        min-height: 38px;
        font: 700 12px 'Segoe UI';
    }
    QFrame#InfoPanel {
        background: rgba(2, 6, 23, 0.34);
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 10px;
    }
    QLabel {
        color: #cbd5e1;
        background: transparent;
        border: none;
        font-family: 'Segoe UI';
    }
    QLabel#BrandName {
        color: #f8fafc;
        font: 800 40px 'Segoe UI';
    }
    QLabel#Title {
        color: #f8fafc;
        font: 800 26px 'Segoe UI';
    }
    QLineEdit {
        background: rgba(15, 23, 42, 0.82);
        border: 1px solid rgba(148, 163, 184, 0.24);
        border-radius: 10px;
        color: #e5e7eb;
        min-height: 40px;
        padding: 0 12px;
        font: 12px 'Segoe UI';
    }
    QLineEdit:focus {
        border-color: rgba(20, 184, 166, 0.72);
    }
    QPushButton {
        background: rgba(15, 23, 42, 0.82);
        border: 1px solid rgba(148, 163, 184, 0.24);
        border-radius: 10px;
        color: #e5e7eb;
        min-height: 40px;
        font: 700 12px 'Segoe UI';
        padding: 0 14px;
    }
    QPushButton:hover {
        background: rgba(51, 65, 85, 0.88);
        border-color: rgba(20, 184, 166, 0.36);
        color: #ffffff;
    }
    QPushButton#PrimaryButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 #14b8c8, stop:1 #3b82f6);
        border: none;
        color: #ffffff;
        font-weight: 800;
    }
    QPushButton#DangerButton:hover {
        background: rgba(244, 63, 94, 0.78);
        border-color: rgba(244, 63, 94, 0.78);
    }
    QPushButton#WindowButton {
        background: transparent;
        border: none;
        border-radius: 16px;
        color: #94a3b8;
        min-height: 32px;
        max-height: 32px;
        min-width: 32px;
        max-width: 32px;
        font-weight: 800;
    }
    QPushButton#WindowButton:hover {
        background: #f43f5e;
        color: #ffffff;
    }
    QListWidget {
        background: rgba(2, 6, 23, 0.50);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 10px;
        color: #e5e7eb;
        outline: none;
        font: 12px 'Segoe UI';
    }
    QListWidget::item {
        color: #94a3b8;
        padding: 10px 12px;
        border-radius: 8px;
        margin: 3px;
    }
    QListWidget::item:selected {
        background: rgba(16, 185, 129, 0.16);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.38);
    }
    QHeaderView::section {
        background: #0f201c;
        color: #e5e7eb;
        border: none;
        padding: 8px;
        font: 700 12px 'Segoe UI';
    }
"""


class AuthShellMixin:
    def _setup_shell(self, root_layout):
        self.setFixedSize(1280, 750)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.drag_pos = QPoint()
        self._dragging_window = False
        self.setStyleSheet(SHELL_STYLE)

        shell = QFrame()
        shell.setObjectName("AuthShell")
        root_layout.addWidget(shell)

        outer_layout = QVBoxLayout(shell)
        outer_layout.setContentsMargins(16, 10, 16, 16)
        outer_layout.setSpacing(0)

        header_layout = QHBoxLayout()
        header_layout.addStretch()
        close_button = QPushButton()
        close_button.setObjectName("WindowButton")
        set_exit_icon(close_button, "#94a3b8", 11)
        close_button.clicked.connect(self.close)
        header_layout.addWidget(close_button)
        outer_layout.addLayout(header_layout)

        shell_layout = QHBoxLayout()
        shell_layout.setContentsMargins(28, 8, 28, 28)
        shell_layout.setSpacing(52)
        outer_layout.addLayout(shell_layout, stretch=1)

        brand = QFrame()
        brand.setObjectName("BrandPanel")
        brand.setFixedWidth(430)
        brand_layout = QVBoxLayout(brand)
        brand_layout.setContentsMargins(34, 34, 34, 34)
        brand_layout.setSpacing(18)
        brand_layout.addStretch()

        logo = QLabel()
        logo.setPixmap(logo_pixmap(230))
        logo.setAlignment(Qt.AlignCenter)
        brand_layout.addWidget(logo)

        name = QLabel("GovSync")
        name.setObjectName("BrandName")
        name.setAlignment(Qt.AlignCenter)
        brand_layout.addWidget(name)

        tag = QLabel("Payroll compliance workspace")
        tag.setAlignment(Qt.AlignCenter)
        tag.setStyleSheet("color: #94a3b8; font: 600 13px 'Segoe UI';")
        brand_layout.addWidget(tag)
        brand_layout.addStretch()

        shell_layout.addWidget(brand)
        return shell_layout

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.position().y() <= 56:
            self.drag_pos = event.globalPosition().toPoint()
            self._dragging_window = True
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging_window and event.buttons() == Qt.LeftButton:
            next_pos = self.pos() + event.globalPosition().toPoint() - self.drag_pos
            self.move(next_pos)
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging_window = False
            self.drag_pos = QPoint()
            event.accept()
            return
        super().mouseReleaseEvent(event)


class LoginDialog(QDialog, AuthShellMixin):
    def __init__(self, controller=None, employer_controller=None):
        super().__init__()
        self.account_role = ""
        self.controller = controller
        self.employer_controller = employer_controller
        self.setWindowTitle("GovSync Login")
        self._setup_ui()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        shell_layout = self._setup_shell(root)

        self.stack = QStackedWidget()
        self.stack.setFixedWidth(470)
        self.stack.setStyleSheet("background: transparent; border: none;")
        self.stack.addWidget(self._login_page())
        self.stack.addWidget(self._register_page())

        # when switching to the register page, refresh employer list
        self.stack.currentChanged.connect(lambda idx: self._populate_employer_combo() if idx == 1 else None)

        shell_layout.addStretch()
        shell_layout.addWidget(self.stack)
        shell_layout.addStretch()

    def showEvent(self, event):
        self._reset_messages()
        super().showEvent(event)

    def _reset_messages(self):
        if hasattr(self, "login_message"):
            self.login_message.clear()
        if hasattr(self, "register_message"):
            self.register_message.clear()

    def _login_page(self):
        panel = QFrame()
        panel.setObjectName("FormPanel")
        panel.setStyleSheet(self._light_form_style())
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(42, 42, 42, 42)
        panel_layout.setSpacing(14)
        panel_layout.addStretch()

        title = QLabel("Login")
        title.setObjectName("Title")
        panel_layout.addWidget(title)

        subtitle = QLabel("Sign in to continue to GovSync.")
        subtitle.setStyleSheet("color: #94a3b8;")
        panel_layout.addWidget(subtitle)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        panel_layout.addWidget(self.username)
        panel_layout.addWidget(self.password)

        self.login_message = QLabel("")
        self.login_message.setStyleSheet("color: #fb7185; font: 700 11px 'Segoe UI';")
        self.login_message.setFixedHeight(20)
        panel_layout.addWidget(self.login_message)

        login_btn = QPushButton("Login")
        login_btn.setObjectName("PrimaryButton")
        login_btn.clicked.connect(self._login)
        panel_layout.addWidget(login_btn)

        register_btn = QPushButton("Create Account")
        register_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        panel_layout.addWidget(register_btn)
        panel_layout.addStretch()
        return panel

    def _register_page(self):
        panel = QFrame()
        panel.setObjectName("FormPanel")
        panel.setStyleSheet(self._light_form_style())
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(34, 34, 34, 34)
        panel_layout.setSpacing(6)
        panel_layout.addStretch()

        title = QLabel("Create Account")
        title.setObjectName("Title")
        title.setStyleSheet("color: #0f172a; font: 800 20px 'Segoe UI';")
        panel_layout.addWidget(title)

        hint = QLabel("Create a username and password for this computer.")
        hint.setStyleSheet("color: #334155; font: 600 11px 'Segoe UI'; margin-bottom: 8px;")
        panel_layout.addWidget(hint)

        self.register_username = QLineEdit()
        self.register_username.setPlaceholderText("Username")
        self.register_username.setStyleSheet("color: #0f172a; background: #ffffff;")
        panel_layout.addWidget(self.register_username)

        self.register_password = QLineEdit()
        self.register_password.setPlaceholderText("Password")
        self.register_password.setEchoMode(QLineEdit.Password)
        self.register_password.setStyleSheet("color: #0f172a; background: #ffffff;")
        panel_layout.addWidget(self.register_password)

        employer_label = QLabel("Employer:")
        employer_label.setStyleSheet("color: #475569; font: 700 10px 'Segoe UI'; text-transform: uppercase;")
        self.register_employer_combo = QComboBox()
        self.register_employer_combo.setStyleSheet("color: #0f172a; background: #ffffff;")
        self.register_employer_combo.setPlaceholderText("Select employer")
        panel_layout.addWidget(employer_label)
        panel_layout.addWidget(self.register_employer_combo)
        self._populate_employer_combo()

        self.register_message = QLabel("")
        self.register_message.setStyleSheet("color: #fb7185; font: 700 11px 'Segoe UI';")
        self.register_message.setWordWrap(True)
        self.register_message.setFixedHeight(38)
        panel_layout.addWidget(self.register_message)

        create_btn = QPushButton("Create Account")
        create_btn.setObjectName("PrimaryButton")
        create_btn.clicked.connect(self._create_account)
        panel_layout.addWidget(create_btn)

        back_btn = QPushButton("Back to Login")
        back_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #475569;
                min-height: 24px;
                font: 600 10px 'Segoe UI';
                text-align: left;
            }
            QPushButton:hover { color: #2563eb; }
        """)
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        panel_layout.addWidget(back_btn)
        panel_layout.addStretch()
        return panel

    def _light_form_style(self):
        return """
            QFrame#FormPanel {
                background: rgba(248, 250, 252, 0.97);
                border: none;
                border-radius: 8px;
            }
            QLabel {
                color: #334155;
                background: transparent;
                border: none;
                font-family: 'Segoe UI';
            }
            QLabel#Title {
                color: #0f172a;
                font: 800 20px 'Segoe UI';
            }
            QLineEdit {
                background: #ffffff;
                border: 1px solid #dbe3ee;
                border-radius: 4px;
                color: #0f172a;
                min-height: 30px;
                padding: 0 10px;
                font: 11px 'Segoe UI';
            }
            QLineEdit:focus {
                border-color: #3b82f6;
            }
            QPushButton {
                background: #eef2f7;
                border: 1px solid #dbe3ee;
                border-radius: 4px;
                color: #0f172a;
                min-height: 32px;
                font: 700 11px 'Segoe UI';
                padding: 0 12px;
            }
            QPushButton:hover {
                background: #e2e8f0;
            }
            QPushButton#PrimaryButton {
                background: #2563eb;
                border: none;
                color: white;
            }
            QPushButton#PrimaryButton:hover {
                background: #1d4ed8;
            }
        """

    def _login(self):
        username = self.username.text().strip()
        password = self.password.text().strip()
        role = authenticate(username, password)
        if not role:
            accounts = load_accounts()
            exists = username == SUPER_ADMIN_USERNAME or any(
                account.get("username") == username for account in accounts
            )
            self.login_message.setText(
                "Invalid credentials." if exists else "Account doesn't exist."
            )
            return
        self.account_role = role
        self.accept()

    def _populate_employer_combo(self):
        _populate_employer_combo(self.register_employer_combo, self.employer_controller)

    def _create_account(self):
        try:
            employer_name, employer_id = _selected_employer_data(self.register_employer_combo)
            _register_account_flow(
                self.controller,
                self.register_username.text(),
                self.register_password.text(),
                employer_name,
                employer_id,
            )
        except ValueError as exc:
            self.register_message.setStyleSheet(
                "color: #fb7185; font: 700 11px 'Segoe UI';"
            )
            self.register_message.setText(str(exc))
            return

        self.register_message.setStyleSheet(
            "color: #86efac; font: 700 11px 'Segoe UI';"
        )
        self.register_message.setText("Account created. You can login now.")
        self.username.setText(self.register_username.text())
        self.password.clear()
        self.stack.setCurrentIndex(0)


class LoginPage(QWidget):
    authenticated = Signal(str, str)

    def __init__(self, parent=None, controller=None, employer_controller=None):
        super().__init__(parent)
        self.controller = controller
        self.employer_controller = employer_controller
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(SHELL_STYLE)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(42, 42, 42, 42)
        layout.setSpacing(0)
        layout.addStretch()

        auth_card = QFrame()
        auth_card.setObjectName("AuthCard")
        auth_card.setFixedSize(900, 520)
        card_layout = QHBoxLayout(auth_card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        brand = QFrame()
        brand.setObjectName("AuthArtPanel")
        brand.setFixedWidth(470)
        brand_layout = QVBoxLayout(brand)
        brand_layout.setContentsMargins(52, 48, 52, 48)
        brand_layout.setSpacing(14)
        brand_layout.addStretch()

        logo = QLabel()
        logo.setPixmap(logo_pixmap(84))
        logo.setAlignment(Qt.AlignLeft)
        brand_layout.addWidget(logo)

        name = QLabel("GovSync")
        name.setObjectName("BrandName")
        name.setAlignment(Qt.AlignLeft)
        brand_layout.addWidget(name)

        tag = QLabel("Payroll compliance workspace")
        tag.setWordWrap(True)
        tag.setStyleSheet("color: #bfdbfe; font: 600 14px 'Segoe UI';")
        brand_layout.addWidget(tag)
        small = QLabel("Automate monthly benefits, reconcile records, and keep contribution work organized.")
        small.setWordWrap(True)
        small.setStyleSheet("color: #94a3b8; font: 11px 'Segoe UI';")
        brand_layout.addWidget(small)
        brand_layout.addStretch()

        self.stack = QStackedWidget()
        self.stack.setFixedWidth(430)
        self.stack.setStyleSheet("background: transparent; border: none;")
        self.stack.addWidget(self._login_page())
        self.stack.addWidget(self._register_page())
        # refresh employer list when register page becomes visible
        self.stack.currentChanged.connect(lambda idx: self._populate_employer_combo() if idx == 1 else None)
        card_layout.addWidget(brand)
        card_layout.addWidget(self.stack)
        layout.addWidget(auth_card, alignment=Qt.AlignCenter)
        layout.addStretch()

    def showEvent(self, event):
        self._reset_messages()
        super().showEvent(event)

    def _reset_messages(self):
        if hasattr(self, "login_message"):
            self.login_message.clear()
        if hasattr(self, "register_message"):
            self.register_message.clear()

    def _login_page(self):
        panel = QFrame()
        panel.setObjectName("FormPanel")
        panel.setStyleSheet(self._auth_form_style())
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(34, 34, 34, 34)
        panel_layout.setSpacing(10)
        panel_layout.addStretch()

        title = QLabel("Login")
        title.setObjectName("Title")
        title.setStyleSheet("color: #0f172a; font: 800 20px 'Segoe UI';")
        panel_layout.addWidget(title)

        subtitle = QLabel("Make your work efficient.")
        subtitle.setStyleSheet("color: #334155; font: 600 11px 'Segoe UI';")
        panel_layout.addWidget(subtitle)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setStyleSheet("color: #0f172a; background: #ffffff;")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setStyleSheet("color: #0f172a; background: #ffffff;")
        self.password.returnPressed.connect(self._login)
        panel_layout.addWidget(self.username)
        panel_layout.addWidget(self.password)

        self.login_message = QLabel("")
        self.login_message.setStyleSheet("color: #fb7185; font: 700 11px 'Segoe UI';")
        self.login_message.setFixedHeight(20)
        panel_layout.addWidget(self.login_message)

        login_btn = QPushButton("Login")
        login_btn.setObjectName("PrimaryButton")
        login_btn.clicked.connect(self._login)
        panel_layout.addWidget(login_btn)

        register_btn = QPushButton("Create Account")
        register_btn.setText("Don't have an account? Sign up")
        register_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #475569;
                min-height: 24px;
                font: 600 10px 'Segoe UI';
                text-align: left;
            }
            QPushButton:hover { color: #2563eb; }
        """)
        register_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        panel_layout.addWidget(register_btn)
        panel_layout.addStretch()
        return panel

    def _register_page(self):
        panel = QFrame()
        panel.setObjectName("FormPanel")
        panel.setStyleSheet(self._auth_form_style())
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(34, 34, 34, 34)
        panel_layout.setSpacing(6)
        panel_layout.addStretch()

        title = QLabel("Create Account")
        title.setObjectName("Title")
        title.setStyleSheet("color: #0f172a; font: 800 20px 'Segoe UI';")
        panel_layout.addWidget(title)

        hint = QLabel("Create a username and password for this computer.")
        hint.setStyleSheet("color: #334155; font: 600 11px 'Segoe UI'; margin-bottom: 8px;")
        panel_layout.addWidget(hint)

        self.register_username = QLineEdit()
        self.register_username.setPlaceholderText("Username")
        self.register_username.setStyleSheet("color: #0f172a; background: #ffffff;")
        panel_layout.addWidget(self.register_username)

        self.register_password = QLineEdit()
        self.register_password.setPlaceholderText("Password")
        self.register_password.setEchoMode(QLineEdit.Password)
        self.register_password.setStyleSheet("color: #0f172a; background: #ffffff;")
        panel_layout.addWidget(self.register_password)

        employer_label = QLabel("Employer:")
        employer_label.setStyleSheet("color: #475569; font: 700 10px 'Segoe UI'; text-transform: uppercase;")
        self.register_employer_combo = QComboBox()
        self.register_employer_combo.setStyleSheet("color: #0f172a; background: #ffffff;")
        self.register_employer_combo.setPlaceholderText("Select employer")
        panel_layout.addWidget(employer_label)
        panel_layout.addWidget(self.register_employer_combo)
        self._populate_employer_combo()

        self.register_message = QLabel("")
        self.register_message.setStyleSheet("color: #fb7185; font: 700 11px 'Segoe UI';")
        self.register_message.setWordWrap(True)
        self.register_message.setFixedHeight(38)
        panel_layout.addWidget(self.register_message)

        create_btn = QPushButton("Create Account")
        create_btn.setObjectName("PrimaryButton")
        create_btn.clicked.connect(self._create_account)
        panel_layout.addWidget(create_btn)

        back_btn = QPushButton("Back to Login")
        back_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #475569;
                min-height: 24px;
                font: 600 10px 'Segoe UI';
                text-align: left;
            }
            QPushButton:hover { color: #2563eb; }
        """)
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        panel_layout.addWidget(back_btn)
        panel_layout.addStretch()
        return panel

    def _auth_form_style(self):
        return """
            QFrame#FormPanel {
                background: rgba(248, 250, 252, 0.98);
                border: none;
                border-radius: 8px;
            }
            QLabel {
                color: #334155;
                background: transparent;
                border: none;
            }
            QLabel#Title {
                color: #0f172a;
                font: 800 20px 'Segoe UI';
            }
            QLineEdit {
                background: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                color: #0f172a;
                min-height: 30px;
                padding: 0 10px;
                font: 11px 'Segoe UI';
            }
            QLineEdit:focus {
                border-color: #2563eb;
            }
            QPushButton {
                background: #eef2f7;
                border: 1px solid #dbe3ee;
                border-radius: 4px;
                color: #0f172a;
                min-height: 32px;
                font: 700 11px 'Segoe UI';
                padding: 0 12px;
            }
            QPushButton:hover {
                background: #e2e8f0;
            }
            QPushButton#PrimaryButton {
                background: #2563eb;
                border: none;
                color: white;
            }
            QPushButton#PrimaryButton:hover {
                background: #1d4ed8;
            }
        """

    def _info_panel(self, title, text):
        panel = QFrame()
        panel.setObjectName("InfoPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #e5e7eb; font: 800 12px 'Segoe UI';")
        body = QLabel(text)
        body.setWordWrap(True)
        body.setStyleSheet("color: #94a3b8; font: 11px 'Segoe UI';")

        layout.addWidget(title_label)
        layout.addWidget(body)
        return panel

    def _login(self):
        username = self.username.text().strip()
        password = self.password.text().strip()
        role = self.controller.login(username, password) if self.controller else authenticate(username, password)
        if not role:
            accounts = load_accounts()
            exists = username == SUPER_ADMIN_USERNAME or any(
                account.get("username") == username for account in accounts
            )
            self.login_message.setText(
                "Invalid credentials." if exists else "Account doesn't exist."
            )
            return
        self.login_message.clear()
        self.authenticated.emit(role, username)

    def _populate_employer_combo(self):
        _populate_employer_combo(self.register_employer_combo, self.employer_controller)

    def _create_account(self):
        try:
            employer_name, employer_id = _selected_employer_data(self.register_employer_combo)
            _register_account_flow(
                self.controller,
                self.register_username.text(),
                self.register_password.text(),
                employer_name,
                employer_id,
            )
        except ValueError as exc:
            self.register_message.setStyleSheet(
                "color: #fb7185; font: 700 11px 'Segoe UI';"
            )
            self.register_message.setText(str(exc))
            return

        self.register_message.setStyleSheet(
            "color: #86efac; font: 700 11px 'Segoe UI';"
        )
        self.register_message.setText("Account created. You can login now.")
        self.username.setText(self.register_username.text())
        self.password.clear()
        self.stack.setCurrentIndex(0)


class SuperAdminPage(QWidget):
    logout_requested = Signal()

    def __init__(self, parent=None, controller=None, employer_controller=None):
        super().__init__(parent)
        self.controller = controller
        self.employer_controller = employer_controller
        self.accounts = []
        self._setup_ui()
        self._load_accounts()

    def _setup_ui(self):
        self.setStyleSheet(SHELL_STYLE)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(18)

        sidebar = QFrame()
        sidebar.setObjectName("ContentPanel")
        sidebar.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(14, 14, 14, 14)
        sidebar_layout.setSpacing(10)

        title = QLabel("Admin")
        title.setObjectName("Title")
        title.setStyleSheet("font: 800 18px 'Segoe UI';")
        sidebar_layout.addWidget(title)

        sub = QLabel("Manage employers and user accounts")
        sub.setWordWrap(True)
        sub.setStyleSheet("color: #94a3b8; font: 600 11px 'Segoe UI';")
        sidebar_layout.addWidget(sub)

        self.nav_list = QListWidget()
        self.nav_list.addItems(["Dashboard", "Employer Creation", "Account List"])
        self.nav_list.setCurrentRow(0)
        self.nav_list.currentRowChanged.connect(self._change_view)
        self.nav_list.setStyleSheet("""
            QListWidget { background: transparent; border: none; padding: 4px; }
            QListWidget::item { padding: 10px 12px; border-radius: 8px; color: #cbd5e1; }
            QListWidget::item:selected { background: rgba(16, 185, 129, 0.18); color: #f8fafc; }
        """)
        sidebar_layout.addWidget(self.nav_list, stretch=1)

        logout_btn = QPushButton("Log Out")
        logout_btn.setObjectName("DangerButton")
        logout_btn.clicked.connect(self.logout_requested.emit)
        sidebar_layout.addWidget(logout_btn)

        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background: transparent; border: none;")
        self.content_stack.addWidget(self._dashboard_page())
        self.content_stack.addWidget(self._employer_page())
        self.content_stack.addWidget(self._account_page())

        self.right_panel = RightPanelWidget(self)
        self.right_panel.setFixedWidth(300)

        layout.addWidget(sidebar)
        layout.addWidget(self.content_stack, stretch=1)
        layout.addWidget(self.right_panel)

    def _dashboard_page(self):
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(16)

        header = QLabel("Dashboard")
        header.setObjectName("Title")
        page_layout.addWidget(header)

        summary = QFrame()
        summary.setObjectName("ContentPanel")
        summary_layout = QVBoxLayout(summary)
        summary_layout.setContentsMargins(20, 20, 20, 20)
        summary_layout.addWidget(QLabel("Overview"))
        summary_layout.addWidget(QLabel("Monitor employer records and accounts from one place."))
        summary_layout.addWidget(QLabel(f"Accounts: {len(self.accounts)}"))
        page_layout.addWidget(summary)
        page_layout.addStretch()
        return page

    def _employer_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        header = QLabel("Employer Creation")
        header.setObjectName("Title")
        layout.addWidget(header)
        layout.addWidget(QLabel("Create and maintain employer records with SSS, PhilHealth, and Pagibig numbers."))
        self.employer_panel = EmployerAdminPanel(controller=self.employer_controller, parent=self)
        layout.addWidget(self.employer_panel, stretch=1)
        return page

    def _account_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        header = QLabel("Account List")
        header.setObjectName("Title")
        sub = QLabel("Review registered accounts and remove them when needed.")
        sub.setStyleSheet("color: #94a3b8;")
        layout.addWidget(header)
        layout.addWidget(sub)

        self.account_count_label = QLabel("0 accounts")
        self.account_count_label.setStyleSheet("color: #94a3b8; font: 600 10px 'Segoe UI';")
        layout.addWidget(self.account_count_label)

        self.account_list = QListWidget()
        self.account_list.currentRowChanged.connect(self._select_account)
        self.account_list.setMinimumHeight(220)
        self.account_list.setStyleSheet("""
            QListWidget { padding: 6px; }
            QListWidget::item { padding: 8px 10px; margin: 2px 0; }
        """)
        layout.addWidget(self.account_list, stretch=1)

        self.table = RoundedTableCard(["Username", "Password", "Employer Name"], self)
        table_header = self.table.horizontalHeader()
        table_header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        table_header.setSectionResizeMode(QHeaderView.Stretch)
        table_header.setStretchLastSection(True)
        self.table.setWordWrap(False)
        self.table.setTextElideMode(Qt.ElideNone)
        layout.addWidget(self.table, stretch=1)

        buttons = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._load_accounts)
        delete_btn = QPushButton("Delete Selected")
        delete_btn.setObjectName("DangerButton")
        delete_btn.clicked.connect(self._delete_selected)
        buttons.addStretch()
        buttons.addWidget(refresh_btn)
        buttons.addWidget(delete_btn)
        layout.addLayout(buttons)
        return page

    def _change_view(self, index):
        self.content_stack.setCurrentIndex(index)

    def _load_accounts(self):
        self.accounts = self.controller.list_accounts() if self.controller else load_accounts()
        if hasattr(self, "account_list"):
            self.account_list.clear()
            for account in self.accounts:
                username = account.username if hasattr(account, "username") else account.get("username", "")
                self.account_list.addItem(username)
        if hasattr(self, "account_count_label"):
            self.account_count_label.setText(f"{len(self.accounts)} account{'s' if len(self.accounts) != 1 else ''}")
        if hasattr(self, "table"):
            self._render_table(self.accounts)
        if hasattr(self, "employer_panel"):
            self.employer_panel.refresh_employers()
        if hasattr(self, "content_stack"):
            self._refresh_dashboard_summary()

    def _refresh_dashboard_summary(self):
        if not hasattr(self, "content_stack"):
            return
        dashboard_page = self.content_stack.widget(0)
        if dashboard_page is None:
            return
        for child in dashboard_page.findChildren(QLabel):
            if child.text().startswith("Accounts:"):
                child.setText(f"Accounts: {len(self.accounts)}")

    def _render_table(self, accounts):
        self.table.setRowCount(len(accounts))
        for row, account in enumerate(accounts):
            username = account.username if hasattr(account, "username") else account.get("username", "")
            employer_name = account.employer_name if hasattr(account, "employer_name") else account.get("employer_name", "")
            self.table.setItem(row, 0, QTableWidgetItem(username))
            self.table.setItem(row, 1, QTableWidgetItem("Protected"))
            self.table.setItem(row, 2, QTableWidgetItem(employer_name))

    def _select_account(self, row):
        if row < 0 or row >= len(self.accounts):
            self._render_table(self.accounts)
            return
        self._render_table([self.accounts[row]])

    def _delete_selected(self):
        row = self.account_list.currentRow()
        if row < 0 or row >= len(self.accounts):
            return

        account = self.accounts[row]
        username = account.username if hasattr(account, "username") else account.get("username", "")
        dialog = GlassDialog(
            self,
            "Delete Account",
            f"Delete account '{username}'?",
            buttons=[
                ("No", lambda: dialog.reject(), False),
                (
                    "Yes",
                    lambda: (
                        self.controller.delete_account(username) if self.controller else delete_account(username),
                        dialog.accept(),
                    ),
                    True,
                ),
            ],
        )
        if dialog.exec() != QDialog.Accepted:
            return

        self._load_accounts()


class RegisterDialog(QDialog, AuthShellMixin):
    def __init__(self, parent=None, controller=None, employer_controller=None):
        super().__init__(parent)
        self.controller = controller
        self.employer_controller = employer_controller
        self.setWindowTitle("Create Account")
        self._setup_ui()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        shell_layout = self._setup_shell(root)

        panel = QFrame()
        panel.setObjectName("FormPanel")
        panel.setFixedWidth(500)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(42, 42, 42, 42)
        panel_layout.setSpacing(10)
        panel_layout.addStretch()

        title = QLabel("Create Account")
        title.setObjectName("Title")
        panel_layout.addWidget(title)

        hint = QLabel("Create a username and password for this computer.")
        hint.setStyleSheet("color: #94a3b8;")
        panel_layout.addWidget(hint)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        panel_layout.addWidget(self.username)
        panel_layout.addWidget(self.password)

        employer_label = QLabel("Employer:")
        self.employer_combo = QComboBox()
        self.employer_combo.setEditable(True)
        self.employer_combo.setInsertPolicy(QComboBox.NoInsert)
        self.employer_combo.setPlaceholderText("Select employer")
        panel_layout.addWidget(employer_label)
        panel_layout.addWidget(self.employer_combo)
        self._populate_employer_combo()

        create_btn = QPushButton("Create Account")
        create_btn.setObjectName("PrimaryButton")
        create_btn.clicked.connect(self._create)
        panel_layout.addWidget(create_btn)

        back_btn = QPushButton("Back to Login")
        back_btn.clicked.connect(self.reject)
        panel_layout.addWidget(back_btn)
        panel_layout.addStretch()

        shell_layout.addStretch()
        shell_layout.addWidget(panel)
        shell_layout.addStretch()

    def _populate_employer_combo(self):
        _populate_employer_combo(self.employer_combo, self.employer_controller)

    def showEvent(self, event):
        # refresh employers each time the dialog is shown
        try:
            self._populate_employer_combo()
        except Exception:
            pass
        super().showEvent(event)

    def _create(self):
        try:
            employer_name, employer_id = _selected_employer_data(self.employer_combo)
            _register_account_flow(
                self.controller,
                self.username.text(),
                self.password.text(),
                employer_name,
                employer_id,
            )
        except ValueError as exc:
            QMessageBox.warning(self, "Invalid Account", str(exc))
            return

        QMessageBox.information(self, "Account Created", "You can now login.")
        self.accept()


class SuperAdminWindow(QWidget, AuthShellMixin):
    logout_requested = Signal()

    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("GovSync Super Admin")
        self._setup_ui()
        self._load_accounts()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        shell_layout = self._setup_shell(root)

        admin_panel = QFrame()
        admin_panel.setObjectName("ContentPanel")
        admin_layout = QHBoxLayout(admin_panel)
        admin_layout.setContentsMargins(22, 22, 22, 22)
        admin_layout.setSpacing(18)

        sidebar = QVBoxLayout()
        sidebar.setSpacing(10)
        title = QLabel("Account List")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.account_count_label = QLabel("0 accounts")
        self.account_count_label.setStyleSheet("color: #94a3b8; font: 600 10px 'Segoe UI';")
        self.account_list = QListWidget()
        self.account_list.currentRowChanged.connect(self._select_account)
        self.account_list.setMinimumWidth(260)
        self.account_list.setMinimumHeight(360)
        self.account_list.setStyleSheet("""
            QListWidget {
                padding: 6px;
            }
            QListWidget::item {
                padding: 8px 10px;
                margin: 2px 0;
            }
        """)

        logout_btn = QPushButton("Log Out")
        logout_btn.setObjectName("DangerButton")
        logout_btn.clicked.connect(self.logout_requested.emit)

        sidebar.addWidget(title)
        sidebar.addWidget(self.account_count_label)
        sidebar.addWidget(self.account_list, stretch=1)
        sidebar.addWidget(logout_btn)

        content = QVBoxLayout()
        header = QLabel("Registered Accounts")
        header.setObjectName("Title")
        sub = QLabel("Super admin can view and delete registered user accounts.")
        sub.setStyleSheet("color: #94a3b8;")

        self.table = RoundedTableCard([
            "Username",
            "Password",
            "SSS Number",
            "PhilHealth Number",
            "HDMF Number",
            "Employer Name",
        ], self)
        table_header = self.table.horizontalHeader()
        table_header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        table_header.setSectionResizeMode(QHeaderView.Stretch)
        table_header.setStretchLastSection(True)
        self.table.setWordWrap(False)
        self.table.setTextElideMode(Qt.ElideNone)
        self.table.setMinimumHeight(380)

        buttons = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._load_accounts)
        delete_btn = QPushButton("Delete Selected")
        delete_btn.setObjectName("DangerButton")
        delete_btn.clicked.connect(self._delete_selected)
        buttons.addStretch()
        buttons.addWidget(refresh_btn)
        buttons.addWidget(delete_btn)

        content.addWidget(header)
        content.addWidget(sub)
        content.addWidget(self.table, stretch=1)
        content.addLayout(buttons)

        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar)
        sidebar_widget.setFixedWidth(290)
        admin_layout.addWidget(sidebar_widget)
        admin_layout.addLayout(content, stretch=1)

        shell_layout.addWidget(admin_panel, stretch=1)

    def _load_accounts(self):
        self.accounts = self.controller.list_accounts() if self.controller else load_accounts()
        self.account_list.clear()
        for account in self.accounts:
            username = account.username if hasattr(account, "username") else account.get("username", "")
            self.account_list.addItem(username)
        self.account_count_label.setText(f"{len(self.accounts)} account{'s' if len(self.accounts) != 1 else ''}")
        self._render_table(self.accounts)

    def _render_table(self, accounts):
        self.table.setRowCount(len(accounts))
        for row, account in enumerate(accounts):
            username = account.username if hasattr(account, "username") else account.get("username", "")
            employer_name = account.employer_name if hasattr(account, "employer_name") else account.get("employer_name", "")
            self.table.setItem(row, 0, QTableWidgetItem(username))
            self.table.setItem(row, 1, QTableWidgetItem("Protected"))
            self.table.setItem(row, 2, QTableWidgetItem(employer_name))

    def _select_account(self, row):
        if row < 0 or row >= len(self.accounts):
            self._render_table(self.accounts)
            return
        self._render_table([self.accounts[row]])

    def _delete_selected(self):
        row = self.account_list.currentRow()
        if row < 0 or row >= len(self.accounts):
            return

        account = self.accounts[row]
        username = account.username if hasattr(account, "username") else account.get("username", "")
        dialog = GlassDialog(
            self,
            "Delete Account",
            f"Delete account '{username}'?",
            buttons=[
                ("No", lambda: dialog.reject(), False),
                (
                    "Yes",
                    lambda: (
                        self.controller.delete_account(username) if self.controller else delete_account(username),
                        dialog.accept(),
                    ),
                    True,
                ),
            ],
        )
        if dialog.exec() != QDialog.Accepted:
            return

        self._load_accounts()
