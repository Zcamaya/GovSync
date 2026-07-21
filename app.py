import os
import sys
import traceback

from PySide6.QtCore import QRect, Qt, QLockFile
from PySide6.QtGui import QFont, QIcon, QImage, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication, QLabel, QMessageBox, QSplashScreen

from config import DATA_DIR
from core.application import GovSyncApplication
from shared.resources import asset_path


_single_instance_lock = None


def acquire_single_instance_lock():
    global _single_instance_lock

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    lock = QLockFile(str(DATA_DIR / "govsync.lock"))
    lock.setStaleLockTime(0)
    if not lock.tryLock(100):
        return False

    _single_instance_lock = lock
    return True


def create_splash():
    logo_path = asset_path("logo.svg")
    if not os.path.exists(logo_path):
        return None

    logo_size = 250
    text_buffer_height = 40
    total_canvas_width = logo_size
    total_canvas_height = logo_size + text_buffer_height

    renderer = QSvgRenderer(logo_path)
    image = QImage(total_canvas_width, total_canvas_height, QImage.Format_ARGB32)
    image.fill(Qt.transparent)

    painter = QPainter(image)
    renderer.render(painter, QRect(0, 0, logo_size, logo_size))
    painter.end()

    splash = QSplashScreen(QPixmap.fromImage(image))

    label = QLabel("Loading GovSync...", splash)
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet("color: white; font-weight: bold;")

    font = QFont()
    font.setPointSize(20)
    label.setFont(font)
    label.setFixedWidth(total_canvas_width)
    label.setFixedHeight(text_buffer_height)
    label.move(0, logo_size)

    return splash


def main():
    splash = None

    try:
        qt_app = QApplication.instance() or QApplication(sys.argv)
        qt_app.setWindowIcon(QIcon(asset_path("icon.ico")))

        # Developer layout debug tool removed. No debug overlays installed.

        if not acquire_single_instance_lock():
            QMessageBox.information(
                None,
                "GovSync",
                "GovSync is already running.",
            )
            return 0

        splash = create_splash()
        if splash:
            splash.show()
            qt_app.processEvents()

        app = GovSyncApplication()
        window = app.create_main_window()
        window.setWindowIcon(QIcon(asset_path("icon.ico")))

        if splash:
            splash.close()

        window.show()
        return qt_app.exec()
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
        error_dialog.exec()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
