from core.application import GovSyncApplication
from qa_tools.qa_engine.page_scanner import PageScanner
from PySide6.QtWidgets import QApplication, QTableWidget, QDialog
from PySide6.QtCore import Qt
import time

app = QApplication.instance() or QApplication([])
application = GovSyncApplication()
window = application.create_main_window()
window.show()
app.processEvents()
nav = window.navigation_controller
nav.on_authenticated('user', 'admin')
app.processEvents()
time.sleep(0.6)
sidebar = window.sidebar_column.list_widget
sidebar.setCurrentRow(2)
app.processEvents()
time.sleep(0.6)
scanner = PageScanner(app, window)
results = scanner._capture_dialogs_from_buttons()
print('results_count', len(results))
for result in results:
    print('label', result.get('label'), 'captured', result.get('captured'))
dialogs = [w for w in app.topLevelWidgets() if isinstance(w, QDialog) and w.isVisible()]
print('visible_dialogs', [(type(d).__name__, d.objectName(), d.windowTitle()) for d in dialogs])
