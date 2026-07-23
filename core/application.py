from PySide6.QtWidgets import QApplication

from config import DEBUG_LAYOUT
from core.dependency_container import build_container
from qa_tools.debug.layout_debug_manager import LayoutDebugManager
from storage.sqlite import initialize_database


class GovSyncApplication:
    def __init__(self):
        self.container = build_container()
        initialize_database(self.container.settings.database_path)
        self.layout_debug_manager = None

    def create_qt_app(self):
        return QApplication.instance() or QApplication([])

    def create_main_window(self):
        from main_window import MainWindow

        window = MainWindow(self.container)
        if self.layout_debug_manager is None:
            self.layout_debug_manager = LayoutDebugManager(self.create_qt_app(), enabled=DEBUG_LAYOUT)
        self.layout_debug_manager.attach_window(window)
        window.layout_debug_manager = self.layout_debug_manager
        return window

    def run(self):
        qt_app = self.create_qt_app()
        window = self.create_main_window()
        window.show()
        return qt_app.exec()
