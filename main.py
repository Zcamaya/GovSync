import os
import sys
import traceback

from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QImage, QPainter, QPixmap, QFont
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication, QMessageBox, QSplashScreen, QLabel

from utils.resources import asset_path


def create_splash():
    logo_path = asset_path("logo.svg")
    if not os.path.exists(logo_path):
        return None

    # 1. Define the logo's intended base size
    logo_size = 250
    # Define how much empty vertical space to add BELOW the logo
    text_buffer_height = 40
    
    total_canvas_width = logo_size
    # Calculate the new total height: 250 logo + 40 text = 290px
    total_canvas_height = logo_size + text_buffer_height

    # 2. Create the expanded, taller canvas image
    renderer = QSvgRenderer(logo_path)
    # image size is now 250x290
    image = QImage(total_canvas_width, total_canvas_height, QImage.Format_ARGB32)
    image.fill(Qt.transparent)
    
    # 3. Create painter and render the SVG asset, but constraint its size!
    painter = QPainter(image)
    # Explicitly render the SVG artwork into ONLY the top 250x250 square.
    # This leaves the bottom 40px completely empty and ensures no stretching.
    renderer.render(painter, QRect(0, 0, logo_size, logo_size))
    painter.end()

    # 4. Use the new, taller pixmap for the splash screen
    splash = QSplashScreen(QPixmap.fromImage(image))
    
    # 5. Attach the text QLabel to the splash screen
    label = QLabel("Loading GovSync...", splash)
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet("color: white; font-weight: bold;")
    
    font = QFont()
    # Increase slightly if desired, as you have more space now
    font.setPointSize(20)
    label.setFont(font)
    
    # Size the text box to fill the buffer zone
    label.setFixedWidth(total_canvas_width) # 250
    label.setFixedHeight(text_buffer_height) # 40
    
    # 6. Push the text box completely past the 250px logo asset.
    # Text now starts at pixel 250, directly in the empty 40px buffer zone.
    # No physical overlap is possible anymore.
    label.move(0, logo_size) 

    return splash


if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = None

    try:
        splash = create_splash()
        if splash:
            splash.show()
            app.processEvents()

        from main_window import MainWindow

        window = MainWindow()

        if splash:
            splash.close()

        window.show()
        sys.exit(app.exec())

    except Exception:
        if splash:
            splash.close()

        error_message = traceback.format_exc()
        print("\n" + "=" * 50)
        print("APP CRASH REGISTERED:")
        print("=" * 50)
        print(error_message)
        print("=" * 50 + "\n")

        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle("GovSync - Crash Report")
        error_dialog.setText("The application failed to launch during initialization.")
        error_dialog.setInformativeText("Review the technical trace details below:")
        error_dialog.setDetailedText(error_message)
        error_dialog.setStandardButtons(QMessageBox.Ok)
        error_dialog.setStyleSheet(
            "QLabel { color: #1e293b; font-family: 'Segoe UI'; font-size: 12px; }"
        )
        error_dialog.exec()
