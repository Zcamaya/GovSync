class AppStyles:
    PANEL_TITLE = "color: #f8fafc; border: none; background: transparent; font: 800 16px 'Segoe UI';"
    SECTION_HEADER = "color: #f8fafc; border: none; background: transparent; font: 800 18px 'Segoe UI';"
    CARD_HEADER = "color: #f8fafc; border: none; background: transparent; font: 800 16px 'Segoe UI';"
    BODY_TEXT = "color: #cbd5e1; border: none; background: transparent; font: 600 12px 'Segoe UI';"
    MUTED_TEXT = "color: #94a3b8; border: none; background: transparent; font: 600 11px 'Segoe UI';"

    CARD_RADIUS = 14
    CONTROL_RADIUS = 10
    SMALL_RADIUS = 8

    PANEL_SPACING = 14
    SECTION_PADDING = 16
    INNER_PADDING = 12

    GLASS_PANEL = """
        QFrame {
            background-color: rgba(20, 30, 45, 0.65);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 14px;
        }
        QLabel {
            background: transparent;
            color: #e2e8f0;
            border: none;
        }
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
        QScrollBar:vertical {
            background: rgba(10, 20, 30, 0.82);
            border: none;
            border-radius: 14px;
            width: 10px;
        }
        QScrollBar::handle:vertical {
            background: rgba(107, 175, 141, 1);
            border-radius: 14px;
            min-height: 28px;
        }
        QScrollBar::handle:vertical:hover {
            background: rgba(107, 175, 141, 0.84);
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
            background: rgba(10, 20, 30, 0.82);
            height: 10px;
            border-radius: 14px;
        }
        QScrollBar::handle:horizontal {
            background: rgba(107, 175, 141, 1);
            border-radius: 14px;
            min-width: 28px;
        }
        QScrollBar::handle:horizontal:hover {
            background: rgba(107, 175, 141, 0.84);
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

    TABLE_SCROLLBAR = """
        QTableWidget QScrollBar:vertical {
            background: rgba(10, 20, 30, 0.82);
            border: none;
            border-radius: 14px;
            width: 10px;
            margin: 44px 0 14px 0;
        }
        QTableWidget QScrollBar::handle:vertical {
            background: rgba(107, 175, 141, 1);
            border-radius: 14px;
            min-height: 28px;
        }
        QTableWidget QScrollBar::handle:vertical:hover {
            background: rgba(107, 175, 141, 0.84);
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
            background: rgba(10, 20, 30, 0.82);
            height: 10px;
            border-radius: 14px;
            margin: 0 12px 12px 12px;
        }
        QTableWidget QScrollBar::handle:horizontal {
            background: rgba(107, 175, 141, 1);
            border-radius: 14px;
            min-width: 28px;
        }
        QTableWidget QScrollBar::handle:horizontal:hover {
            background: rgba(107, 175, 141, 0.84);
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
            background: rgba(8, 18, 28, 0.96);
            alternate-background-color: rgba(10, 20, 30, 0.84);
            color: #e5e7eb;
            gridline-color: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(59, 130, 246, 0.10);
            border-radius: 16px;
            font: 11px 'Segoe UI';
        }
        QTableWidget::viewport {
            border-radius: 16px;
            background: transparent;
        }
        QTableWidget::pane {
            border-radius: 16px;
            background: transparent;
        }
        QTableWidget QTableCornerButton {
            background: transparent;
            border: none;
        }
        QHeaderView::section {
            background: rgba(8, 18, 28, 0.98);
            color: #f8fafc;
            font: 700 12px 'Segoe UI';
            padding: 14px 16px;
            border: none;
            text-align: left;
        }
        QHeaderView::section:first-of-type {
            border-top-left-radius: 16px;
        }
        QHeaderView::section:last-of-type {
            border-top-right-radius: 16px;
        }
        QTableWidget::item {
            padding: 12px 16px;
            border: none;
        }
        QTableWidget::item:alternate {
            background: rgba(10, 20, 30, 0.82);
        }
        QTableWidget::item:selected {
            background: rgba(20, 184, 166, 0.24);
            color: #ffffff;
        }
    """
