from core.application import GovSyncApplication
from PySide6.QtWidgets import QApplication, QDialog, QTableWidget
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
time.sleep(2.0)
panel = window.workspace_stack.widget(2)
table = panel.table
print('panel', type(panel).__name__, panel.objectName())
print('table_rows', table.rowCount())
print('current_employee_rows', len(table._current_employee_rows))
emp = table.get_current_employee(0)
print('emp0', emp)
print('item0_0', table.item(0,0).text() if table.item(0,0) else None)
print('item0_2', table.item(0,2).text() if table.item(0,2) else None)
if emp:
    print('calling show_details now')
    panel._show_details(emp)
    print('returned from show_details')
    app.processEvents()
    time.sleep(1.0)
    dialogs = [w for w in app.topLevelWidgets() if isinstance(w, QDialog) and w.isVisible()]
    print('dialogs', [(type(d).__name__, d.objectName(), d.windowTitle()) for d in dialogs])
