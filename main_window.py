from PySide6.QtCore import QPoint, Qt, QEvent
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
)

from core.navigation_controller import NavigationController
from core.page_factory import PageFactory
from core.window_state_manager import WindowStateManager
from widgets.glass_dialog import GlassDialog
from shared.ui import set_exit_icon, set_maximize_icon, set_minimize_icon
from config import APP_NAME, DEFAULT_WINDOW_HEIGHT, DEFAULT_WINDOW_WIDTH, MIN_WINDOW_HEIGHT, MIN_WINDOW_WIDTH
from shared.resources import asset_path


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
        self.container.setStyleSheet(self._container_style(False))
        self._was_maximized_before_minimize = False
        self._build_ui()

    def _container_style(self, maximized: bool) -> str:
        radius = 0 if maximized else 20
        css = """
            #MainContainer {
                background: qradialgradient(cx:0.3, cy:0.2, radius:1.4, fx:0.3, fy:0.2,
                                            stop:0 #0a1f1a, stop:0.5 #070b12, stop:1 #020408);
                border: 1px solid rgba(20, 184, 166, 0.16);
                border-radius: {radius}px;
            }
            QLabel {
                font-family: 'Segoe UI', sans-serif;
                background: transparent;
                color: white;
            }
            QScrollBar:vertical {
                background: rgba(2, 6, 23, 0.18);
                border: none;
                border-radius: 14px;
                width: 12px;
                margin: 3px;
            }
            QScrollBar::handle:vertical {
                background: rgba(148, 163, 184, 0.46);
                border-radius: 14px;
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
                border-radius: 14px;
                height: 12px;
                margin: 3px;
            }
            QScrollBar::handle:horizontal {
                background: rgba(148, 163, 184, 0.46);
                border-radius: 14px;
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
        """
        return css.replace("{radius}", str(radius))

    def _build_ui(self):
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

        self.window_state_manager = WindowStateManager(self)
        self._update_maximized_style()

        page_factory = PageFactory(self.app_container)
        self.login_page, self.admin_page = page_factory.create_auth_pages()
        (
            self.app_page,
            self.sidebar_column,
            self.right_column,
            self.workspace_stack,
            self.workspace_widget,
            self.earnings_panel,
            self.employee_records_panel,
            self.philhealth_panel,
            self.sss_panel,
            self.hdmf_panel,
        ) = page_factory.create_app_page()

        self.page_stack.addWidget(self.login_page)
        self.page_stack.addWidget(self.admin_page)
        self.page_stack.addWidget(self.app_page)

        self.navigation_controller = NavigationController(
            self.page_stack,
            self.sidebar_column,
            self.right_column,
            self.workspace_stack,
            self.workspace_widget,
            self.earnings_panel,
            self.employee_records_panel,
            self.philhealth_panel,
            self.sss_panel,
            self.hdmf_panel,
            self.login_page,
            self.admin_page,
            self.app_page,
        )
        self.navigation_controller.bind()
        self.sidebar_column.logout_requested.connect(self.navigation_controller.show_login)
        self.navigation_controller.initial_authentication()
        self.drag_pos = QPoint()

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
        self.window_state_manager.toggle_maximized()
        self._update_maximized_style()

    def showMaximized(self):
        super().showMaximized()
        self._update_maximized_style()
        self.window_state_manager.update_lock_state(True)

    def showNormal(self):
        super().showNormal()
        self._update_maximized_style()
        self.window_state_manager.update_lock_state(False)

    def showMinimized(self):
        self._was_maximized_before_minimize = self.isMaximized() or bool(self.windowState() & Qt.WindowMaximized)
        super().showMinimized()
        self._update_maximized_style()
        self.window_state_manager.update_lock_state(False)

    def _update_maximized_style(self):
        maximized = bool(self.windowState() & Qt.WindowMaximized)
        self.container.setStyleSheet(self._container_style(maximized))
        self.container.update()
        if hasattr(self, "window_state_manager"):
            self.window_state_manager.update_lock_state(maximized)

    def mousePressEvent(self, event):
        self.window_state_manager.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.window_state_manager.mouseMoveEvent(event)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.WindowStateChange:
            if self._was_maximized_before_minimize and not self.isMinimized() and not self.isMaximized():
                super().showMaximized()
                self._was_maximized_before_minimize = False
            self._update_maximized_style()
        elif event.type() == QEvent.ActivationChange:
            self._update_maximized_style()

    def closeEvent(self, event):
        self.window_state_manager.closeEvent(event)
