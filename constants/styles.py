class AppStyles:
    PANEL_TITLE = "color: #f8fafc; border: none; background: transparent; font: 800 16px 'Segoe UI';"
    SECTION_HEADER = "color: #f8fafc; border: none; background: transparent; font: 800 18px 'Segoe UI';"
    CARD_HEADER = "color: #f8fafc; border: none; background: transparent; font: 800 16px 'Segoe UI';"

    GLASS_PANEL = """
        QFrame {
            background-color: rgba(20, 30, 45, 0.65);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 15px;
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
            border-bottom-left-radius: 16px;
            border-bottom-right-radius: 16px;
        }
    """

    NOTE_ROW = """
        QFrame#NoteRow {
            background: transparent;
            border: none;
        }
        QFrame#NoteTitleBar {
            background: rgba(10, 18, 32, 0.98);
            border: 1px solid rgba(45, 212, 191, 0.18);
            border-radius: 10px;
        }
        QFrame#NoteTitleBar:hover {
            border-color: rgba(45, 212, 191, 0.34);
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
