# widgets/glass_panel.py
from PySide6.QtWidgets import QFrame
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect

class TrueGlassPanel(QFrame):
    def __init__(self, border_radius=18, parent=None):
        super().__init__(parent)
        # Ensure proper rendering with rounded borders
        self.setLineWidth(0)
        self.setFrameStyle(QFrame.NoFrame)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(20, 30, 45, 0.65);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: {border_radius}px;
            }}
            QLabel {{ 
                background: transparent; 
                border: none;
                outline: none;
            }}
        """)
        glow = QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(15)
        glow.setColor(QColor(16, 185, 129, 25)) 
        glow.setOffset(0, 0)
        self.setGraphicsEffect(glow)