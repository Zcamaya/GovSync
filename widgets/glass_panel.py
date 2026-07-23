# widgets/glass_panel.py
from PySide6.QtGui import QColor, QPainterPath
from PySide6.QtCore import QRectF
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect
from PySide6.QtGui import QRegion

from shared.constants.styles import AppStyles


class TrueGlassPanel(QFrame):
    def __init__(self, border_radius=14, parent=None):
        super().__init__(parent)
        self._radius = int(border_radius)
        self.setLineWidth(0)
        self.setFrameStyle(QFrame.NoFrame)

        panel_style = AppStyles.GLASS_PANEL.replace("border-radius: 14px;", f"border-radius: {self._radius}px;")
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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        rect = self.rect()
        if rect.width() <= 0 or rect.height() <= 0:
            return
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), self._radius, self._radius)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))