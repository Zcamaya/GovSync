from core.application import GovSyncApplication
from PySide6.QtWidgets import QApplication, QDialog, QTableWidget
from PySide6.QtTest import QTest
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
time.sleep(0.8)
sidebar = window.sidebar_column.list_widget
sidebar.setCurrentRow(2)
app.processEvents()
time.sleep(0.8)
print('page_index', window.workspace_stack.currentIndex())
tables = [w for w in app.allWidgets() if isinstance(w, QTableWidget) and w.isVisible()]
print('tables', len(tables))
for table in tables:
    print('table', type(table).__name__, table.objectName(), 'rows', table.rowCount(), 'cols', table.columnCount())
    if table.rowCount() > 0:
        row = 0
        col = 0
        table.setCurrentCell(row, col)
        index = table.model().index(row, col)
        rect = table.visualRect(index)
        print('rect', rect)
        QTest.mouseDClick(table.viewport(), Qt.LeftButton, Qt.NoModifier, rect.center())
        app.processEvents()
        time.sleep(0.8)
        dialogs = [w for w in app.topLevelWidgets() if isinstance(w, QDialog) and w.isVisible()]
        print('dialogs', [(type(d).__name__, d.objectName(), d.windowTitle()) for d in dialogs])
