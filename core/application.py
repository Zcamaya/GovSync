from PySide6.QtWidgets import QApplication

from core.dependency_container import build_container
from storage.sqlite import initialize_database


class GovSyncApplication:
    def __init__(self):
        self.container = build_container()
        initialize_database(self.container.settings.database_path)

    def create_qt_app(self):
        return QApplication.instance() or QApplication([])

    def create_main_window(self):
        from main_window import MainWindow

        return MainWindow(self.container)

    def run(self):
        qt_app = self.create_qt_app()
        window = self.create_main_window()
        window.show()
        return qt_app.exec()
