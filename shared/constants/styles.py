class AppStyles:
    WINDOW_MARGIN = 12
    PAGE_MARGIN = 16
    PANEL_SPACING = 14
    PANEL_SPACING_COMPACT = 10
    SECTION_PADDING = 16
    INNER_PADDING = 12
    TABLE_CARD_PADDING = 12
    DIALOG_PADDING = 16
    SIDEBAR_WIDTH = 240
    RIGHT_PANEL_MIN_WIDTH = 320
    NOTIFICATION_MARGIN = 16
    NOTIFICATION_GAP = 8

    PANEL_TITLE = "color: #f8fafc; border: none; background: transparent; font: 800 16px 'Segoe UI';"
    SECTION_HEADER = "color: #f8fafc; border: none; background: transparent; font: 800 18px 'Segoe UI';"
    CARD_HEADER = "color: #f8fafc; border: none; background: transparent; font: 800 16px 'Segoe UI';"
    BODY_TEXT = "color: #cbd5e1; border: none; background: transparent; font: 600 12px 'Segoe UI';"
    MUTED_TEXT = "color: #94a3b8; border: none; background: transparent; font: 600 11px 'Segoe UI';"

    TABLE_SURFACE = "#0f172a"
    TABLE_SURFACE_ALT = "#0b1220"
    TABLE_BORDER = "rgba(148, 163, 184, 0.18)"
    TABLE_TEXT = "#e5e7eb"
    TABLE_MUTED = "#94a3b8"
    TABLE_ACCENT = "#2dd4bf"
    TABLE_HOVER = "rgba(59, 130, 246, 0.16)"
    TABLE_ACTIVE = "rgba(20, 184, 166, 0.24)"
    TABLE_DISABLED = "rgba(226, 232, 240, 0.38)"
    TABLE_ROW_HEIGHT = 38
    TABLE_HEADER_HEIGHT = 44
    TABLE_CELL_PADDING = 12
    TABLE_SECTION_GAP = 12

    SCREEN_TITLE = "color: #f8fafc; font: 800 22px 'Segoe UI';"
    SECTION_TITLE = "color: #f8fafc; font: 700 15px 'Segoe UI';"
    SECTION_SUBTITLE = "color: #94a3b8; font: 600 12px 'Segoe UI';"
    TABLE_TITLE = "color: #f8fafc; font: 800 14px 'Segoe UI';"
    TABLE_HEADER_TEXT = "color: #f8fafc; font: 700 12px 'Segoe UI';"
    TABLE_BODY_TEXT = "color: #e5e7eb; font: 600 12px 'Segoe UI';"
    TABLE_METADATA_TEXT = "color: #94a3b8; font: 600 11px 'Segoe UI';"
    PANEL_BORDER_SUBTLE = "rgba(148, 163, 184, 0.16)"
    SURFACE_ELEVATED = "rgba(20, 30, 45, 0.70)"
    SURFACE_BORDER = "rgba(255, 255, 255, 0.12)"
    METRIC_VALUE = "color: #34d399; border: none; background: transparent; font: 800 28px 'Segoe UI';"

    FIELD_INPUT = """
        QLineEdit, QComboBox, QTextEdit {
            background: rgba(15, 23, 42, 0.82);
            color: #f8fafc;
            border: 1px solid rgba(148, 163, 184, 0.24);
            border-radius: 10px;
            padding: 8px 12px;
            font: 600 12px 'Segoe UI';
        }
        QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
            border: 1px solid rgba(45, 212, 191, 0.65);
            background: rgba(15, 23, 42, 0.96);
        }
    """

    TABLE_SEARCH_INPUT = FIELD_INPUT

    NAV_LIST = """
        QListWidget {
            background: transparent;
            border: none;
            outline: none;
        }
        QListWidget::item {
            color: #94a3b8;
            padding: 12px 16px;
            font: 600 13px 'Segoe UI';
            border-radius: 12px;
            margin-bottom: 4px;
        }
        QListWidget::item:hover {
            background-color: rgba(255, 255, 255, 0.04);
            color: #f1f5f9;
        }
        QListWidget::item:selected {
            background-color: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.4);
        }
    """

    TABLE_PAGINATION_BUTTON = """
        QPushButton {
            background: rgba(15, 23, 42, 0.82);
            color: #f8fafc;
            border: 1px solid rgba(148, 163, 184, 0.24);
            border-radius: 10px;
            padding: 8px 14px;
            font: 700 11px 'Segoe UI';
            min-height: 34px;
        }
        QPushButton:hover:!disabled {
            background: rgba(51, 65, 85, 0.92);
            border-color: rgba(148, 163, 184, 0.42);
            color: #ffffff;
        }
        QPushButton:disabled {
            color: rgba(226, 232, 240, 0.38);
            background: rgba(15, 23, 42, 0.5);
            border-color: rgba(148, 163, 184, 0.12);
        }
    """

    TABLE_STAT_CARD = """
        QFrame {
            background: rgba(15, 23, 42, 0.56);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
        }
    """

    CARD_RADIUS = 14
    CONTROL_RADIUS = 10
    SMALL_RADIUS = 8

    GLASS_PANEL = f"""
        QFrame {{
            background-color: {SURFACE_ELEVATED};
            border: 1px solid {SURFACE_BORDER};
            border-radius: 14px;
        }}
        QLabel {{
            background: transparent;
            color: #e2e8f0;
            border: none;
        }}
    """
    
    ACTION_BUTTON = """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #06b6d4, stop:1 #3b82f6);
            border: none;
            border-radius: 10px;
            color: white;
            font-weight: bold;
            padding: 10px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0891b2, stop:1 #2563eb);
        }
    """

    PRIMARY_BUTTON = """
        QPushButton {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 #14b8c8,
                stop:1 #3b82f6
            );
            border: none;
            border-radius: 10px;
            color: #ffffff;
            font: 800 12px 'Segoe UI';
            min-height: 38px;
            padding: 0 18px;
        }
        QPushButton:hover {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 #22d3ee,
                stop:1 #2563eb
            );
        }
        QPushButton:disabled {
            background: rgba(30, 41, 59, 0.58);
            color: rgba(226, 232, 240, 0.45);
        }
    """

    SECONDARY_BUTTON = """
        QPushButton {
            background: rgba(30, 41, 59, 0.76);
            border: 1px solid rgba(148, 163, 184, 0.24);
            border-radius: 10px;
            color: #e5e7eb;
            font: 700 12px 'Segoe UI';
            min-height: 38px;
            padding: 0 16px;
        }
        QPushButton:hover {
            background: rgba(51, 65, 85, 0.92);
            border-color: rgba(148, 163, 184, 0.36);
            color: #ffffff;
        }
        QPushButton:disabled {
            background: rgba(15, 23, 42, 0.48);
            color: rgba(226, 232, 240, 0.42);
        }
    """

    ACCENT_BUTTON = """
        QPushButton {
            background: rgba(20, 184, 166, 0.16);
            border: 1px solid rgba(20, 184, 166, 0.34);
            border-radius: 8px;
            color: #d1fae5;
            font: 800 11px 'Segoe UI';
            padding: 0 12px;
        }
        QPushButton:hover {
            background: rgba(20, 184, 166, 0.24);
            border-color: rgba(45, 212, 191, 0.46);
            color: #ffffff;
        }
        QPushButton:disabled {
            background: rgba(15, 23, 42, 0.48);
            border-color: rgba(148, 163, 184, 0.18);
            color: rgba(226, 232, 240, 0.42);
        }
    """

    DANGER_ICON_BUTTON = """
        QToolButton, QPushButton {
            background: rgba(244, 63, 94, 0.96);
            border: none;
            border-radius: 10px;
            color: #ffffff;
            font: 900 18px 'Segoe UI';
        }
        QToolButton:hover, QPushButton:hover {
            background: rgba(251, 113, 133, 0.98);
        }
    """

    DIALOG_CLOSE_BUTTON = """
        QPushButton {
            background: rgba(30, 41, 59, 0.76);
            border: 1px solid rgba(148, 163, 184, 0.24);
            border-radius: 10px;
            color: #f8fafc;
            font: 800 12px 'Segoe UI';
        }
        QPushButton:hover {
            background: rgba(244, 63, 94, 0.32);
            border-color: rgba(244, 63, 94, 0.56);
        }
    """

    SQUARE_CLOSE_BUTTON = """
        QPushButton {
            background: rgba(15, 23, 42, 0.86);
            border: 1px solid rgba(148, 163, 184, 0.20);
            border-radius: 8px;
            color: #93c5fd;
            font: 900 13px 'Segoe UI';
            padding: 0;
        }
        QPushButton:hover {
            background: rgba(30, 41, 59, 0.92);
            border-color: rgba(147, 197, 253, 0.42);
            color: #dbeafe;
        }
    """

    HISTORY_SURFACE = """
        QFrame#HistoryDetailCard, QDialog {
            background: rgba(8, 20, 18, 0.96);
            border: 1px solid rgba(20, 184, 166, 0.20);
            border-radius: 14px;
        }
        QScrollBar:vertical {
            background: rgba(2, 6, 23, 0.24);
            border: none;
            border-radius: 14px;
            width: 10px;
            margin: 2px;
        }
        QScrollBar::handle:vertical {
            background: rgba(148, 163, 184, 0.42);
            border-radius: 14px;
            min-height: 20px;
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
        QTabWidget::pane {
            background: rgba(2, 6, 23, 0.30);
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 10px;
            top: -1px;
        }
        QTabBar::tab {
            background: rgba(15, 23, 42, 0.66);
            color: #94a3b8;
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-bottom: none;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            min-width: 120px;
            padding: 8px 14px;
            font: 700 12px 'Segoe UI';
        }
        QTabBar::tab:selected {
            background: rgba(20, 43, 37, 0.90);
            color: #e5e7eb;
            border-color: rgba(20, 184, 166, 0.34);
        }
        QTableWidget {
            background: rgba(2, 6, 23, 0.46);
            alternate-background-color: rgba(15, 23, 42, 0.52);
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 10px;
            color: #e5e7eb;
            gridline-color: rgba(148, 163, 184, 0.14);
            selection-background-color: rgba(20, 184, 166, 0.26);
            selection-color: #ffffff;
            font: 11px 'Segoe UI';
        }
        QHeaderView::section {
            background: rgba(2, 6, 23, 0.78);
            border: none;
            border-right: 1px solid rgba(148, 163, 184, 0.16);
            color: #cbd5e1;
            font: 700 11px 'Segoe UI';
            padding: 7px 8px;
        }
    """

    @staticmethod
    def danger_ghost_button(radius=10, font_size=14):
        return f"""
            QToolButton, QPushButton {{
                background: rgba(30, 41, 59, 0.76);
                border: 1px solid rgba(148, 163, 184, 0.24);
                border-radius: {radius}px;
                color: #f8fafc;
                font: 900 {font_size}px 'Segoe UI';
            }}
            QToolButton:hover, QPushButton:hover {{
                background: rgba(244, 63, 94, 0.32);
                border-color: rgba(244, 63, 94, 0.56);
                color: #ffffff;
            }}
        """

    DIALOG_BASE = """
        QDialog {
            background: transparent;
        }
        QLabel#DialogTitle {
            color: #f8fafc;
            font: 800 18px 'Segoe UI';
        }
        QLabel#DialogSubtitle {
            color: #94a3b8;
            font: 600 12px 'Segoe UI';
        }
        QFrame#DialogCard {
            background: qradialgradient(cx:0.2, cy:0.1, radius:1.2,
                                        stop:0 rgba(20, 43, 37, 0.98),
                                        stop:0.55 rgba(8, 20, 18, 0.98),
                                        stop:1 rgba(2, 6, 23, 0.99));
            border: 1px solid rgba(20, 184, 166, 0.22);
            border-radius: 16px;
        }
        QLabel {
            color: #e5e7eb;
            background: transparent;
            border: none;
            font: 700 12px 'Segoe UI';
        }
        QLabel#DialogTitle {
            color: #f8fafc;
            font: 800 18px 'Segoe UI';
        }
        QLineEdit, QTextEdit {
            background: rgba(2, 6, 23, 0.58);
            border: 1px solid rgba(148, 163, 184, 0.22);
            border-radius: 9px;
            color: #e5e7eb;
            padding: 8px 10px;
            font: 12px 'Segoe UI';
        }
        QLineEdit:focus, QTextEdit:focus {
            border-color: rgba(20, 184, 166, 0.72);
        }
        QToolButton {
            background: rgba(30, 41, 59, 0.76);
            border: 1px solid rgba(148, 163, 184, 0.24);
            border-radius: 8px;
            color: #e5e7eb;
            min-height: 32px;
            min-width: 32px;
            font: 800 11px 'Segoe UI';
        }
        QToolButton:hover {
            background: rgba(51, 65, 85, 0.92);
            border-color: rgba(148, 163, 184, 0.36);
        }
        QPushButton {
            background: rgba(30, 41, 59, 0.76);
            border: 1px solid rgba(148, 163, 184, 0.24);
            border-radius: 10px;
            color: #e5e7eb;
            min-height: 38px;
            font: 700 12px 'Segoe UI';
            padding: 0 16px;
        }
        QPushButton:hover {
            background: rgba(51, 65, 85, 0.92);
            border-color: rgba(148, 163, 184, 0.36);
            color: #ffffff;
        }
        QPushButton#PrimaryButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #14b8c8, stop:1 #3b82f6);
            border: none;
            color: #ffffff;
            font-weight: 800;
        }
        QPushButton#PrimaryButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #22d3ee, stop:1 #2563eb);
        }
        QFrame#ButtonBar {
            background: rgba(255, 255, 255, 0.03);
            border: none;
            border-top: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 12px;
        }
    """

    NOTE_ROW = """
        QFrame#NoteRow {
            background: rgba(8, 14, 26, 0.95);
            border: 1px solid rgba(56, 75, 114, 0.36);
            border-radius: 10px;
        }
        QFrame#NoteRow:hover {
            border-color: rgba(59, 130, 246, 0.48);
            background: rgba(10, 18, 38, 0.96);
        }
        QLabel {
            border: none;
            background: transparent;
        }
    """

    @staticmethod
    def danger_icon_button(radius=10):
        return f"""
            QToolButton, QPushButton {{
                background: rgba(244, 63, 94, 0.96);
                border: none;
                border-radius: {radius}px;
                color: #ffffff;
                font: 900 18px 'Segoe UI';
            }}
            QToolButton:hover, QPushButton:hover {{
                background: rgba(251, 113, 133, 0.98);
            }}
        """

    GLOBAL_DROPDOWN = """
        QComboBox {
            background: rgba(15, 23, 42, 0.78);
            color: #f8fafc;
            border: 1px solid rgba(148, 163, 184, 0.28);
            border-radius: 8px;
            padding: 6px 10px;
            font: 11px 'Segoe UI';
        }
        QComboBox:hover {
            border: 1px solid rgba(148, 163, 184, 0.42);
            background: rgba(15, 23, 42, 0.88);
        }
        QComboBox:focus {
            border: 2px solid rgba(59, 130, 246, 0.62);
            background: rgba(15, 23, 42, 0.92);
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox::down-arrow {
            image: none;
            width: 0;
            height: 0;
        }
        QComboBox QAbstractItemView {
            background: rgba(15, 23, 42, 0.95);
            color: #f8fafc;
            border: 1px solid rgba(59, 130, 246, 0.34);
            border-radius: 8px;
            selection-background-color: rgba(59, 130, 246, 0.48);
            outline: none;
        }
        QComboBox QAbstractItemView::item {
            padding: 6px 10px;
            border: none;
        }
        QComboBox QAbstractItemView::item:selected {
            background: rgba(59, 130, 246, 0.48);
            color: #ffffff;
        }
        QComboBox QAbstractItemView::item:hover {
            background: rgba(59, 130, 246, 0.34);
        }
    """

    SCROLLBAR = """
        QTableWidget QScrollBar:vertical {
            background: transparent;
            border: none;
            width: 8px;
            margin: 4px 2px 4px 0px;
        }
        QTableWidget QScrollBar::handle:vertical {
            background: rgba(107, 175, 141, 0.36);
            border-radius: 6px;
            min-height: 24px;
        }
        QTableWidget QScrollBar::handle:vertical:hover {
            background: rgba(107, 175, 141, 0.56);
        }
        QTableWidget QScrollBar::add-line:vertical,
        QTableWidget QScrollBar::sub-line:vertical,
        QTableWidget QScrollBar::add-page:vertical,
        QTableWidget QScrollBar::sub-page:vertical {
            background: transparent;
            border: none;
            height: 0;
        }
        QTableWidget QScrollBar:horizontal {
            background: transparent;
            border: none;
            height: 8px;
            margin: 0px 4px 2px 4px;
        }
        QTableWidget QScrollBar::handle:horizontal {
            background: rgba(107, 175, 141, 0.36);
            border-radius: 6px;
            min-width: 24px;
        }
        QTableWidget QScrollBar::handle:horizontal:hover {
            background: rgba(107, 175, 141, 0.56);
        }
        QTableWidget QScrollBar::add-line:horizontal,
        QTableWidget QScrollBar::sub-line:horizontal,
        QTableWidget QScrollBar::add-page:horizontal,
        QTableWidget QScrollBar::sub-page:horizontal {
            background: transparent;
            border: none;
            width: 0;
        }
    """

    UNIFIED_TAB_STYLE = """
        QTabWidget::pane {
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 10px;
            background: rgba(8, 20, 18, 0.32);
            top: -1px;
        }
        QTabBar::tab {
            background: rgba(15, 23, 42, 0.62);
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-bottom: none;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            color: #94a3b8;
            min-width: 130px;
            padding: 9px 16px;
            font: 700 12px 'Segoe UI';
        }
        QTabBar::tab:selected {
            background: rgba(20, 43, 37, 0.82);
            color: #e5e7eb;
            border-color: rgba(20, 184, 166, 0.34);
        }
        QTabBar::tab:hover {
            color: #e5e7eb;
        }
    """

    TABLE_SCROLLBAR = """
        QTableWidget QScrollBar:vertical {
            background: transparent;
            border: none;
            width: 8px;
            margin: 0 0 4px 0;
        }
        QTableWidget QScrollBar::handle:vertical {
            background: rgba(107, 175, 141, 0.24);
            border-radius: 6px;
            min-height: 24px;
        }
        QTableWidget QScrollBar::handle:vertical:hover,
        QTableWidget QScrollBar::handle:vertical:pressed {
            background: rgba(107, 175, 141, 0.42);
        }
        QTableWidget QScrollBar::add-line:vertical,
        QTableWidget QScrollBar::sub-line:vertical,
        QTableWidget QScrollBar::add-page:vertical,
        QTableWidget QScrollBar::sub-page:vertical {
            background: transparent;
            border: none;
            height: 0;
        }
        QTableWidget QScrollBar:horizontal {
            background: transparent;
            border: none;
            height: 8px;
            margin: 0px 4px 2px 4px;
        }
        QTableWidget QScrollBar::handle:horizontal {
            background: rgba(107, 175, 141, 0.24);
            border-radius: 6px;
            min-width: 24px;
        }
        QTableWidget QScrollBar::handle:horizontal:hover,
        QTableWidget QScrollBar::handle:horizontal:pressed {
            background: rgba(107, 175, 141, 0.42);
        }
        QTableWidget QScrollBar::add-line:horizontal,
        QTableWidget QScrollBar::sub-line:horizontal,
        QTableWidget QScrollBar::add-page:horizontal,
        QTableWidget QScrollBar::sub-page:horizontal {
            background: transparent;
            border: none;
            width: 0;
        }
    """

    TABLE_BASE = """
        QTableWidget {
            background: rgba(10, 18, 32, 0.92);
            alternate-background-color: rgba(11, 22, 40, 0.95);
            color: #e5e7eb;
            gridline-color: rgba(148, 163, 184, 0.08);
            border: 1px solid rgba(71, 85, 105, 0.35);
            border-radius: 14px;
            font: 600 12px 'Segoe UI';
        }
        QTableWidget::viewport {
            border-top-left-radius: 14px;
            border-top-right-radius: 14px;
            border-bottom-left-radius: 14px;
            border-bottom-right-radius: 14px;
            background: rgba(10, 18, 32, 0.92);
        }
        QTableWidget::pane {
            border-top-left-radius: 0px;
            border-top-right-radius: 0px;
            border-bottom-left-radius: 14px;
            border-bottom-right-radius: 14px;
            background: transparent;
        }
        QHeaderView {
            border: none;
            background: transparent;
        }
        QTableWidget QTableCornerButton {
            background: transparent;
            border: none;
        }
        QHeaderView::section {
            background: rgba(15, 23, 42, 0.98);
            color: #f8fafc;
            font: 700 12px 'Segoe UI';
            padding: 12px 14px;
            min-height: 42px;
            border: none;
            border-bottom: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 0px;
            margin: 0px;
            text-align: left;
        }
        QHeaderView::section:first-of-type {
            border-top-left-radius: 0px;
        }
        QHeaderView::section:last-of-type {
            border-top-right-radius: 0px;
        }
        QTableWidget::item {
            padding: 10px 14px;
            border: none;
            border-bottom: 1px solid rgba(148, 163, 184, 0.10);
        }
        QTableWidget::item:alternate {
            background: rgba(10, 18, 32, 0.85);
        }
        QTableWidget::item:hover {
            background: rgba(255, 255, 255, 0.04);
        }
        QTableWidget::item:selected,
        QTableWidget::item:selected:active {
            background: rgba(20, 184, 166, 0.18);
            color: #ffffff;
        }
    """

    TABLE_CARD = """
        QFrame#TableCard {
            background: rgba(8, 14, 26, 0.96);
            border: 1px solid rgba(71, 85, 105, 0.45);
            border-radius: 18px;
        }
        QFrame#TableCard:hover {
            border-color: rgba(59, 130, 246, 0.36);
        }
    """

    TABLE_CANONICAL = TABLE_BASE + TABLE_SCROLLBAR + """
        QTableWidget {
            border: 1px solid rgba(71, 85, 105, 0.42);
            border-radius: 14px;
        }
        QTableWidget::viewport {
            border-top-left-radius: 14px;
            border-top-right-radius: 14px;
            border-bottom-left-radius: 14px;
            border-bottom-right-radius: 14px;
            background: transparent;
        }
        QTableWidget QTableCornerButton {
            background: transparent;
            border: none;
        }
        QTableWidget QHeaderView {
            border: none;
            background: transparent;
        }
        QTableWidget QHeaderView::section {
            background: rgba(15, 23, 42, 0.98);
            color: #f8fafc;
            padding: 12px 14px;
            min-height: 42px;
            border: none;
            border-bottom: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 0px;
            font: 700 12px 'Segoe UI';
            text-align: left;
            margin: 0px;
        }
        QTableWidget QHeaderView::section:first-of-type {
            border-top-left-radius: 14px;
        }
        QTableWidget QHeaderView::section:last-of-type {
            border-top-right-radius: 14px;
        }
        QTableWidget QScrollBar:vertical {
            background: transparent;
            width: 8px;
            margin: 4px 2px 4px 0px;
        }
        QTableWidget QScrollBar::handle:vertical {
            background: rgba(107, 175, 141, 0.24);
            border-radius: 6px;
            min-height: 24px;
        }
        QTableWidget QScrollBar::handle:vertical:hover {
            background: rgba(107, 175, 141, 0.42);
        }
        QTableWidget QScrollBar:horizontal {
            background: transparent;
            height: 8px;
            margin: 0px 4px 2px 4px;
        }
        QTableWidget QScrollBar::handle:horizontal {
            background: rgba(107, 175, 141, 0.24);
            border-radius: 6px;
            min-width: 24px;
        }
        QTableWidget QScrollBar::handle:horizontal:hover {
            background: rgba(107, 175, 141, 0.42);
        }
        QTableWidget::item:alternate {
            background: rgba(10, 18, 32, 0.84);
        }
    """
