# widgets/glass_panel.py
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect

from shared.constants.styles import AppStyles


class TrueGlassPanel(QFrame):
    def __init__(self, border_radius=14, parent=None):
        super().__init__(parent)
        self.setLineWidth(0)
        self.setFrameStyle(QFrame.NoFrame)

        panel_style = AppStyles.GLASS_PANEL.replace("border-radius: 14px;", f"border-radius: {border_radius}px;")
        panel_style += """
            QLabel {
                background: transparent;
                border: none;
                outline: none;
            }
        """
        self.setStyleSheet(panel_style)

        glow = QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(12)
        glow.setColor(QColor(16, 185, 129, 20))
        glow.setOffset(0, 0)
        self.setGraphicsEffect(glow)